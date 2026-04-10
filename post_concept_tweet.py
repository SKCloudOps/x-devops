"""
Daily DevOps/Cloud Concept Explainer Bot
Generates a 4-tweet thread explaining a concept like you would in an interview.
Uses Claude API and X API v2.
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
CONCEPTS = [
    "aws_networking",
    "kubernetes_architecture",
    "cicd_pipelines",
    "infrastructure_as_code",
    "container_fundamentals",
    "cloud_security",
    "monitoring_observability",
    "serverless_computing",
    "devops_practices",
    "linux_fundamentals",
    "git_version_control",
    "load_balancing_scaling",
    "database_fundamentals",
    "dns_and_routing",
    "secrets_management",
    "service_mesh",
    "configuration_management",
    "disaster_recovery",
    "api_gateway_patterns",
    "logging_and_tracing",
]

SYSTEM_PROMPT = """You are a DevOps engineer explaining concepts on X (Twitter) in a thread. 
Imagine someone in an interview asked you "explain X" — that's the vibe. Clear, confident, 
practical. You're helping engineers actually understand things, not just memorize definitions.

Write a 4-tweet thread:
- Tweet 1 (hook): Grab attention. Use a bold statement, analogy, or "most people can't explain this 
  clearly" angle. State what you're explaining. 1-2 hashtags.
- Tweet 2 (what it is): Plain English explanation. No textbook definitions. Explain it like you're 
  talking to a colleague over coffee. Use an analogy if it helps.
- Tweet 3 (real world): How it actually works in production. A real scenario, common gotcha, or 
  "here's what actually matters." This is what separates you in an interview.
- Tweet 4 (pro tip): One actionable takeaway, a lesser-known fact, or interview tip. End with 
  1-2 hashtags.

Voice rules:
- Sound like a real person. Use contractions, casual language, short sentences.
- NO words like "crucial", "essential", "leverage", "comprehensive", "robust", "utilizing"
- NO "Let's dive in", "Let me explain", "Here's a thread" — just start talking
- Have opinions. Be direct. Fragment sentences are fine.
- Each tweet MUST be under 270 characters. This is NON-NEGOTIABLE.

Respond ONLY in this exact JSON format, no markdown fences:
{
  "tweet_1": "hook tweet",
  "tweet_2": "explanation tweet",
  "tweet_3": "real world tweet",
  "tweet_4": "pro tip tweet",
  "concept": "concept name"
}"""


MAX_TWEET_LENGTH = 280
MAX_RETRIES = 3


def get_todays_concept() -> str:
    """Rotate through concepts based on day of year."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return CONCEPTS[day_of_year % len(CONCEPTS)]


def truncate_to_limit(text: str, limit: int = MAX_TWEET_LENGTH) -> str:
    """Truncate text to fit within character limit, breaking at last sentence boundary."""
    if len(text) <= limit:
        return text
    truncated = text[:limit]
    for sep in [". ", "! ", "? "]:
        last_sep = truncated.rfind(sep)
        if last_sep > limit // 2:
            return truncated[: last_sep + 1].rstrip()
    last_space = truncated.rfind(" ")
    if last_space > limit // 2:
        return truncated[:last_space].rstrip() + "…"
    return truncated[:limit - 1] + "…"


def _call_claude_with_retry(client, system_prompt: str, messages: list,
                            max_api_retries: int = 5, base_delay: float = 2.0):
    """Call Claude API with exponential backoff for transient errors."""
    for api_attempt in range(1, max_api_retries + 1):
        try:
            return client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=800,
                system=system_prompt,
                messages=messages,
            )
        except anthropic.APIStatusError as e:
            if e.status_code in (429, 500, 502, 503, 504, 529):
                if api_attempt == max_api_retries:
                    print(f"Claude API failed after {max_api_retries} attempts.")
                    raise
                delay = base_delay * (2 ** (api_attempt - 1))
                print(f"Claude API error (HTTP {e.status_code}), retrying in {delay}s... "
                      f"(attempt {api_attempt}/{max_api_retries})")
                time.sleep(delay)
            else:
                raise


def generate_content(concept: str) -> dict:
    """Use Claude API to generate a 4-tweet concept thread."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Add variety with a sub-topic seed
    seed_keyword = random.choice([
        "EKS", "Lambda", "Terraform", "GitHub Actions", "Helm", "VPC",
        "IAM", "S3", "Aurora", "DynamoDB", "Prometheus", "Grafana",
        "Docker", "Kubernetes", "Jenkins", "ArgoCD", "Ansible", "Vault",
        "CloudWatch", "Route53", "ALB", "NLB", "EC2", "ECS", "Fargate",
        "SNS", "SQS", "API Gateway", "CloudFront", "Redis", "RDS",
        "Nginx", "HAProxy", "Terraform modules", "Helm charts",
    ])

    user_prompt = f"""Concept area: {concept}
Sub-topic inspiration (use as a starting point): {seed_keyword}
Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

Pick ONE specific concept from the area above and explain it in a 4-tweet thread.
STRICT LIMIT: every tweet must be under 270 characters. Count carefully."""

    messages = [{"role": "user", "content": user_prompt}]
    tweet_keys = ["tweet_1", "tweet_2", "tweet_3", "tweet_4"]

    for attempt in range(1, MAX_RETRIES + 1):
        message = _call_claude_with_retry(client, SYSTEM_PROMPT, messages)

        response_text = message.content[0].text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        content = json.loads(response_text)

        # Check all tweets are within limit
        lengths = {k: len(content[k]) for k in tweet_keys}
        over_limit = {k: v for k, v in lengths.items() if v > MAX_TWEET_LENGTH}

        if not over_limit:
            return content

        print(f"Attempt {attempt}/{MAX_RETRIES}: over limit — {over_limit} — retrying...")

        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": message.content[0].text},
            {"role": "user", "content": (
                f"These tweets exceed the limit: {over_limit}. "
                f"ALL tweets MUST be under {MAX_TWEET_LENGTH} characters. "
                f"Shorten them and respond in the same JSON format."
            )},
        ]

    # Final fallback: truncate
    print("Max retries exceeded — truncating content to fit limits.")
    for key in tweet_keys:
        content[key] = truncate_to_limit(content[key])
    return content


def post_thread(tweets: list[str]) -> dict:
    """Post a thread of tweets using X API v2."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    tweet_ids = []

    # Post first tweet
    first = client.create_tweet(text=tweets[0])
    first_id = first.data["id"]
    tweet_ids.append(first_id)
    print(f"Posted tweet 1/4: {first_id}")

    # Post remaining tweets as replies in the thread
    previous_id = first_id
    for i, tweet_text in enumerate(tweets[1:], start=2):
        reply = client.create_tweet(text=tweet_text, in_reply_to_tweet_id=previous_id)
        reply_id = reply.data["id"]
        tweet_ids.append(reply_id)
        previous_id = reply_id
        print(f"Posted tweet {i}/4: {reply_id}")

    return {"tweet_ids": tweet_ids}


def log_posted_content(content: dict, tweet_ids: dict):
    """Append to history log for dedup and tracking."""
    log_file = Path("concept_history.json")
    history = []
    if log_file.exists():
        history = json.loads(log_file.read_text())

    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "concept": content["concept"],
        "tweet_1": content["tweet_1"],
        "tweet_2": content["tweet_2"],
        "tweet_3": content["tweet_3"],
        "tweet_4": content["tweet_4"],
        "tweet_ids": tweet_ids.get("tweet_ids", []),
        "content_hash": hashlib.md5(content["tweet_1"].encode()).hexdigest(),
    }
    history.append(entry)
    log_file.write_text(json.dumps(history, indent=2))
    print(f"Logged entry #{len(history)}")


def main():
    concept = get_todays_concept()
    print(f"Today's concept area: {concept}")

    # Generate content
    content = generate_content(concept)
    tweet_keys = ["tweet_1", "tweet_2", "tweet_3", "tweet_4"]
    for key in tweet_keys:
        print(f"{key} ({len(content[key])} chars): {content[key]}")

    # Validate lengths
    for key in tweet_keys:
        assert len(content[key]) <= MAX_TWEET_LENGTH, f"{key} too long: {len(content[key])}"

    tweets = [content[key] for key in tweet_keys]

    # Post to X (skip if DRY_RUN is set)
    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN — skipping post to X")
        tweet_ids = {"tweet_ids": ["dry_run"] * 4}
    else:
        tweet_ids = post_thread(tweets)

    # Log
    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
