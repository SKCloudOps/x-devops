"""
Daily DevOps/Cloud/Platform Engineering Tweet Bot
Generates and posts a tweet + threaded reply using Claude API and X API v2.
"""

import os
import json
import random
import hashlib
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

SYSTEM_PROMPT = """You are a senior Cloud/DevOps/Platform Engineering practitioner who posts daily 
educational content on X (Twitter). Your audience is mid-to-senior engineers preparing for interviews 
or leveling up their skills.

Rules:
- Tweet 1 (main): Must be under 270 characters. Ask a compelling interview question OR state a 
  trending topic with a hot take. Use 1-2 relevant hashtags. No emojis except sparingly.
- Tweet 2 (reply): Must be under 270 characters. Give a concise, authoritative answer or deeper 
  insight. Sound like a real engineer, not AI. Include a practical detail or real-world context.
- Never start with "Great question" or similar filler.
- Avoid generic advice. Be specific and opinionated.
- Write like a human — short sentences, direct, occasional sentence fragments are fine.

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

Generate today's tweet and reply. STRICT LIMIT: each must be under 270 characters. Count carefully."""

    messages = [{"role": "user", "content": user_prompt}]

    for attempt in range(1, MAX_RETRIES + 1):
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=messages,
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
        "category": content["category"],
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
