"""
Daily DevOps/Cloud/Platform Engineering Tweet Bot
Generates and posts a single tweet (interview Q&A) using Claude API and X API v2.
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

SYSTEM_PROMPT = """You are a Platform/Cloud/DevOps engineer sharing COMMONLY ASKED interview questions 
on X (Twitter). The classics that come up in EVERY interview.

SOUND HUMAN — THIS IS THE #1 RULE:
- Write like you're typing a quick tweet on your phone during a coffee break
- Be conversational. Imperfect. Natural. The way real people actually tweet.
- Use contractions always (don't, can't, it's, won't, wouldn't, shouldn't)
- Vary sentence length. Mix short fragments with slightly longer ones.
- It's okay to start sentences with "And", "But", "So", "Like", "Honestly"
- Add personality — mild sarcasm, humor, or a personal touch

HUMAN writing examples (DO this):
  "Interviewer: 'What's the diff between a Pod and a Container?' Lol I blanked on this in my first k8s interview ngl"
  "Interviewer: 'Explain how a load balancer works' — sounds easy till you're actually standing there trying to explain it"

BOT writing examples (NEVER do this):
  "Interview Question: Can you explain the fundamental differences between Security Groups and NACLs in AWS?"
  "Here's a commonly asked DevOps interview question about Kubernetes orchestration"

BANNED WORDS/PHRASES (instant bot giveaway):
- "crucial", "essential", "leverage", "comprehensive", "robust", "utilizing", "fundamental"
- "ensure", "facilitate", "optimize", "implement", "streamline", "enhance"
- "In today's", "It's important to", "Here's why", "Let me explain"
- "This is a great question", "Great question!", "Key takeaway"
- Don't write in complete perfect grammar — real tweets aren't essays
- No bullet points or numbered lists inside tweets

FORMAT — THIS IS CRITICAL FOR ENGAGEMENT:
On X, posts over 280 characters show a "Show more" button. We want the QUESTION visible 
and the ANSWER hidden behind the fold so users have to click to see it.

Structure the tweet EXACTLY like this:
1. ABOVE THE FOLD (first 280 characters — this is what people see in their feed):
   - "Interviewer:" followed by the question in quotes
   - A short teaser reaction like "most people get this wrong" or "sounds easy right?"
   - Keep this part UNDER 260 characters to be safe

2. Then add TWO blank lines (line breaks) to create visual separation

3. BELOW THE FOLD (hidden behind "Show more"):
   - The answer, written casually like you're telling a friend
   - Include a real-world tip, gotcha, or common mistake
   - End with 3-5 relevant hashtags

Example structure:
Interviewer: "What's the diff between Docker and a VM?" — sounds basic but most people fumble this one

[blank line]
[blank line]
Docker shares the host OS kernel so containers are lightweight and start in ms. VMs run a full OS copy = way more overhead. That's why you can run 50 containers where 5 VMs would choke.

#Docker #DevOps #CloudComputing #InterviewTips

QUESTION STYLE — FREQUENTLY ASKED, NOT OBSCURE:
- Questions asked in 8 out of 10 interviews. The ones people Google the night before.
- AVOID niche, obscure, or ultra-specific questions

LENGTH: You have X Premium. Tweet can be up to 2000 characters total.
The question part (above fold) should be under 260 characters.
The answer part (below fold) can be 200-600 characters.

Respond ONLY in this exact JSON format, no markdown fences.
Use \\n for line breaks in the JSON string:
{
  "tweet": "question part\\n\\n\\nanswer part\\n\\n#hashtags",
  "category": "category label"
}"""

POLL_PROMPT = """You are a Platform/Cloud/DevOps engineer creating a multiple-choice interview 
question poll on X (Twitter). Polls get MASSIVE engagement -- people love testing themselves.

SOUND HUMAN:
- Write the question casually, like you're quizzing a friend
- Use contractions, keep it natural
- Add a short teaser like "most people pick the wrong one" or "this trips up even seniors"

RULES:
- The question text must be UNDER 260 characters (it's visible in the feed)
- Provide exactly 4 answer options, each MUST be UNDER 25 characters (X poll limit)
- Only ONE option should be correct
- Make the wrong options plausible -- not obviously wrong
- Add 3-5 hashtags at the end of the question text
- Pick COMMONLY ASKED interview questions, not obscure ones

BANNED WORDS: "crucial", "essential", "leverage", "comprehensive", "fundamental"

Respond ONLY in this exact JSON format, no markdown fences:
{
  "tweet": "the question text with hashtags",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "category": "category label"
}"""


def get_todays_category() -> str:
    """Rotate through categories based on day of year."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return CATEGORIES[day_of_year % len(CATEGORIES)]


MAX_TWEET_LENGTH = 2000  # X Premium allows up to 4000, keeping 2000 for readability
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
                max_tokens=1000,
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
    """Use Claude API to generate a single tweet with Q&A, with retries for length violations."""
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
and engineers prep for the night before. Start with "Interviewer:" then the question in quotes,
then include the answer in the SAME tweet.
You have X Premium — tweet can be up to 2000 characters. Aim for 500-1000 chars.
Use the space for a solid Q&A with real detail."""

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

        if tweet_len <= MAX_TWEET_LENGTH:
            return content

        print(f"Attempt {attempt}/{MAX_RETRIES}: tweet={tweet_len} chars — retrying...")

        # Build retry conversation asking Claude to shorten
        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": message.content[0].text},
            {"role": "user", "content": (
                f"The tweet is {tweet_len} chars. "
                f"It MUST be under {MAX_TWEET_LENGTH} characters. "
                f"Shorten it and respond in the same JSON format."
            )},
        ]

    # Final fallback: truncate to fit
    print("Max retries exceeded — truncating content to fit limits.")
    content["tweet"] = truncate_to_limit(content["tweet"])
    return content


def generate_poll_content(category: str) -> dict:
    """Use Claude API to generate a poll-style interview question."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    seed_word = random.choice([
        "EKS", "Lambda", "Terraform", "ArgoCD", "GitHub Actions", "Helm",
        "VPC", "IAM", "CloudFront", "DynamoDB", "Prometheus", "Docker",
        "Kubernetes", "Route53", "S3", "EC2", "Fargate", "ECS",
        "CloudFormation", "Ansible", "Jenkins", "Vault", "Grafana",
    ])

    user_prompt = f"""Category: {category}
Seed keyword (inspiration, don't force it): {seed_word}
Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

Create a multiple-choice poll question for a DevOps/Cloud interview.
Question text MUST be under 260 characters. Each option MUST be under 25 characters.
Make it a commonly asked question that most engineers would recognize."""

    messages = [{"role": "user", "content": user_prompt}]

    for attempt in range(1, MAX_RETRIES + 1):
        message = _call_claude_with_retry(client, POLL_PROMPT, messages)

        response_text = message.content[0].text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        content = json.loads(response_text)

        tweet_len = len(content["tweet"])
        options = content.get("options", [])
        options_valid = (len(options) == 4 and
                        all(len(opt) <= 25 for opt in options))

        if tweet_len <= MAX_TWEET_LENGTH and options_valid:
            return content

        print(f"Poll attempt {attempt}/{MAX_RETRIES}: tweet={tweet_len} chars, "
              f"options_valid={options_valid} -- retrying...")

        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": message.content[0].text},
            {"role": "user", "content": (
                f"Issues: tweet is {tweet_len} chars (must be under {MAX_TWEET_LENGTH}). "
                f"Each poll option must be under 25 characters. "
                f"Fix and respond in the same JSON format."
            )},
        ]

    # Truncate tweet if needed, return as-is for options
    content["tweet"] = truncate_to_limit(content["tweet"])
    return content


def post_to_x(tweet_text: str, poll_options: list = None) -> dict:
    """Post a tweet (optionally with a poll) using X API v2 via tweepy."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    kwargs = {"text": tweet_text}
    if poll_options:
        kwargs["poll_options"] = poll_options
        kwargs["poll_duration_minutes"] = 1440  # 24 hours

    tweet = client.create_tweet(**kwargs)
    tweet_id = tweet.data["id"]
    post_type = "poll" if poll_options else "tweet"
    print(f"Posted {post_type}: {tweet_id}")

    return {"tweet_id": tweet_id}


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
        "tweet_id": tweet_ids.get("tweet_id"),
        "content_hash": hashlib.md5(content["tweet"].encode()).hexdigest(),
    }
    history.append(entry)
    log_file.write_text(json.dumps(history, indent=2))
    print(f"Logged entry #{len(history)}")


def main():
    category = get_todays_category()
    print(f"Today's category: {category}")

    # Post a poll once per day at the 12:00 PM CDT slot (17:00 UTC)
    # All other time slots get regular Q&A
    current_hour = datetime.now(timezone.utc).hour
    use_poll = current_hour == 17

    if use_poll:
        print("Mode: POLL")
        content = generate_poll_content(category)
        poll_options = content.get("options", [])
        print(f"Generated poll ({len(content['tweet'])} chars): {content['tweet']}")
        print(f"Options: {poll_options}")

        assert len(content["tweet"]) <= MAX_TWEET_LENGTH, f"Tweet too long: {len(content['tweet'])}"

        if os.environ.get("DRY_RUN", "false").lower() == "true":
            print("DRY RUN -- skipping post to X")
            tweet_ids = {"tweet_id": "dry_run"}
        else:
            tweet_ids = post_to_x(content["tweet"], poll_options=poll_options)

        content["type"] = "poll"
    else:
        print("Mode: Q&A")
        content = generate_content(category)
        print(f"Generated tweet ({len(content['tweet'])} chars): {content['tweet']}")

        assert len(content["tweet"]) <= MAX_TWEET_LENGTH, f"Tweet too long: {len(content['tweet'])}"

        if os.environ.get("DRY_RUN", "false").lower() == "true":
            print("DRY RUN -- skipping post to X")
            tweet_ids = {"tweet_id": "dry_run"}
        else:
            tweet_ids = post_to_x(content["tweet"])

        content["type"] = "qa"

    # Log
    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
