"""
Daily DevOps/Cloud/Platform Engineering Tweet Bot
Generates and posts a tweet + threaded reply using Claude API and X API v2.
"""

import os
import json
import random
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import tweepy


# --- Configuration ---
CATEGORIES = [
    "aws_interview_question",
    "kubernetes_interview_question",
    "cicd_interview_question",
    "platform_engineering_interview_question",
    "terraform_iac_interview_question",
    "devops_trending_topic",
    "cloud_architecture_pattern",
    "sre_observability_question",
    "networking_security_question",
    "container_orchestration_question",
]

SYSTEM_PROMPT = """You are a Platform/Cloud/DevOps engineer sharing the most COMMONLY ASKED interview questions 
on X (Twitter). These are the questions that come up in EVERY interview — the classics that 
engineers Google the night before. Your goal is maximum engagement through relatability.

FORMAT RULE — MANDATORY:
- Tweet 1 (main) MUST start with "Interviewer:" followed by the question in quotes.
  Example: Interviewer: "What's the difference between a Pod and a Container in Kubernetes?"
- After the question, add a one-liner reaction like "This one catches 80% of candidates" 
  or "Sounds simple but most people fumble this"
- Then add 3-5 relevant hashtags

QUESTION STYLE — FREQUENTLY ASKED, NOT OBSCURE:
- Pick questions that are asked in 8 out of 10 DevOps/Cloud interviews
- The kind of questions people search on Google/Reddit before interviews
- Questions where people THINK they know the answer but often get it wrong
- Examples of the RIGHT kind of questions:
  * "What happens when you type kubectl apply?"
  * "Explain the difference between SG and NACL"
  * "What's a VPC and why do you need one?"
  * "How does a load balancer decide where to send traffic?"
  * "What's the difference between Docker and a VM?"
  * "Explain blue-green vs canary deployment"
  * "What is Infrastructure as Code and why does it matter?"
  * "How do you handle secrets in a CI/CD pipeline?"
- AVOID niche, obscure, or ultra-specific questions that only 1% of engineers face

Voice & tone:
- Write like a REAL person. Casual. Use contractions (don't, can't, it's, won't).
- Short punchy sentences. The reaction after the question should make people go 
  "oh no, do I actually know this?"
- Make it relatable — everyone's been in that interview hot seat

NEVER do these:
- Words: "crucial", "essential", "leverage", "comprehensive", "robust", "utilizing"
- Don't make the question too long or multi-part
- Don't ask about super niche services or tools nobody uses
- Generic CTAs: "What do you think?", "Agree or disagree?"

Format:
- Tweet 1 (main): Under 270 characters. Starts with "Interviewer:" + question + brief reaction + hashtags.
- Tweet 2 (reply): Under 270 characters. A clear, concise answer that actually helps people. 
  Include a practical tip or common mistake. Add 3-5 relevant hashtags at the end.
- Hashtag examples: #AWS #DevOps #Kubernetes #CloudComputing #Docker #Terraform #CICD #SRE #Linux
  #PlatformEngineering #InfraAsCode #GitOps #CloudNative #InterviewTips #TechTwitter

Respond ONLY in this exact JSON format, no markdown fences:
{
  "tweet": "the main tweet text",
  "reply": "the threaded reply text",
  "category": "category label"
}"""


def get_todays_category() -> str:
    """Rotate through categories based on day of year."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return CATEGORIES[day_of_year % len(CATEGORIES)]


MAX_TWEET_LENGTH = 280
MAX_RETRIES = 3


def truncate_to_limit(text: str, limit: int = MAX_TWEET_LENGTH) -> str:
    """Truncate text to fit within character limit, breaking at last sentence boundary."""
    if len(text) <= limit:
        return text
    # Try to break at the last sentence-ending punctuation within limit
    truncated = text[:limit]
    for sep in [". ", "! ", "? "]:
        last_sep = truncated.rfind(sep)
        if last_sep > limit // 2:  # Only break if we keep at least half the content
            return truncated[: last_sep + 1].rstrip()
    # Fallback: break at last space and add ellipsis
    last_space = truncated.rfind(" ")
    if last_space > limit // 2:
        return truncated[:last_space].rstrip() + "…"
    return truncated[:limit - 1] + "…"

def _call_claude_with_retry(client, system_prompt: str, messages: list,
                            max_api_retries: int = 5, base_delay: float = 2.0):
    """Call Claude API with exponential backoff for transient errors (429, 5xx, 529)."""
    for api_attempt in range(1, max_api_retries + 1):
        try:
            return client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=system_prompt,
                messages=messages,
            )
        except anthropic.APIStatusError as e:
            # Retry on rate limit (429), server errors (5xx), and overloaded (529)
            if e.status_code in (429, 500, 502, 503, 504, 529):
                if api_attempt == max_api_retries:
                    print(f"Claude API failed after {max_api_retries} attempts.")
                    raise
                delay = base_delay * (2 ** (api_attempt - 1))  # 2s, 4s, 8s, 16s, 32s
                print(f"Claude API error (HTTP {e.status_code}), retrying in {delay}s... "
                      f"(attempt {api_attempt}/{max_api_retries})")
                time.sleep(delay)
            else:
                raise  # Don't retry client errors (400, 401, 403, 404, etc.)


def generate_content(category: str) -> dict:
    """Use Claude API to generate tweet + reply, with retries for length violations."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Add some randomness to avoid repetitive patterns
    seed_word = random.choice([
        "EKS", "Lambda", "Terraform", "ArgoCD", "GitHub Actions", "Helm",
        "VPC", "IAM", "CloudFront", "Aurora", "DynamoDB", "Prometheus",
        "Grafana", "Istio", "Crossplane", "Backstage", "Karpenter",
        "IRSA", "OPA", "Cilium", "Flux", "Tekton", "Vault", "KEDA",
        "CloudFormation", "CDK", "Pulumi", "Docker", "Podman", "Buildpacks",
        "Service Mesh", "API Gateway", "SQS", "SNS", "EventBridge",
        "Step Functions", "Fargate", "ECS", "Route53", "WAF", "Shield",
        "GuardDuty", "SecurityHub", "Config", "CloudTrail", "KMS",
    ])

    user_prompt = f"""Category: {category}
Seed keyword (use this as inspiration, don't force it): {seed_word}
Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

Generate a FREQUENTLY ASKED interview question — the kind that shows up in most interviews 
and engineers prep for the night before. Start with "Interviewer:" then the question in quotes.
STRICT LIMIT: each tweet must be under 270 characters. Count carefully."""

    messages = [{"role": "user", "content": user_prompt}]

    for attempt in range(1, MAX_RETRIES + 1):
        message = _call_claude_with_retry(
            client, SYSTEM_PROMPT, messages
        )

        response_text = message.content[0].text.strip()
        # Clean potential markdown fences
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        content = json.loads(response_text)

        tweet_len = len(content["tweet"])
        reply_len = len(content["reply"])

        if tweet_len <= MAX_TWEET_LENGTH and reply_len <= MAX_TWEET_LENGTH:
            return content

        print(f"Attempt {attempt}/{MAX_RETRIES}: tweet={tweet_len}, reply={reply_len} chars — retrying...")

        # Build retry conversation asking Claude to shorten
        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": message.content[0].text},
            {"role": "user", "content": (
                f"The content exceeds the character limit. "
                f"Tweet is {tweet_len} chars, reply is {reply_len} chars. "
                f"Both MUST be under {MAX_TWEET_LENGTH} characters. "
                f"Shorten them and respond in the same JSON format."
            )},
        ]

    # Final fallback: truncate to fit
    print("Max retries exceeded — truncating content to fit limits.")
    content["tweet"] = truncate_to_limit(content["tweet"])
    content["reply"] = truncate_to_limit(content["reply"])
    return content


def post_to_x(tweet_text: str, reply_text: str) -> dict:
    """Post tweet and threaded reply using X API v2 via tweepy."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    # Post main tweet
    main_tweet = client.create_tweet(text=tweet_text)
    main_tweet_id = main_tweet.data["id"]
    print(f"Posted main tweet: {main_tweet_id}")

    # Post reply in thread
    reply_tweet = client.create_tweet(
        text=reply_text, in_reply_to_tweet_id=main_tweet_id
    )
    reply_tweet_id = reply_tweet.data["id"]
    print(f"Posted reply: {reply_tweet_id}")

    return {
        "main_tweet_id": main_tweet_id,
        "reply_tweet_id": reply_tweet_id,
    }


def log_posted_content(content: dict, tweet_ids: dict):
    """Append to history log for dedup and tracking."""
    log_file = Path("tweet_history.json")
    history = []
    if log_file.exists():
        history = json.loads(log_file.read_text())

    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "category": content.get("category", "unknown"),
        "tweet": content["tweet"],
        "reply": content["reply"],
        "main_tweet_id": tweet_ids.get("main_tweet_id"),
        "reply_tweet_id": tweet_ids.get("reply_tweet_id"),
        "content_hash": hashlib.md5(content["tweet"].encode()).hexdigest(),
    }
    history.append(entry)
    log_file.write_text(json.dumps(history, indent=2))
    print(f"Logged entry #{len(history)}")


def main():
    category = get_todays_category()
    print(f"Today's category: {category}")

    # Generate content
    content = generate_content(category)
    print(f"Generated tweet ({len(content['tweet'])} chars): {content['tweet']}")
    print(f"Generated reply ({len(content['reply'])} chars): {content['reply']}")

    # Validate lengths
    assert len(content["tweet"]) <= 280, f"Tweet too long: {len(content['tweet'])}"
    assert len(content["reply"]) <= 280, f"Reply too long: {len(content['reply'])}"

    # Post to X (skip if DRY_RUN is set)
    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN — skipping post to X")
        tweet_ids = {"main_tweet_id": "dry_run", "reply_tweet_id": "dry_run"}
    else:
        tweet_ids = post_to_x(content["tweet"], content["reply"])

    # Log
    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
