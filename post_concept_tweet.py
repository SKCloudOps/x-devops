"""
Daily DevOps/Cloud Concept Explainer Bot
Generates and posts a single tweet explaining a concept like you would in an interview.
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

SYSTEM_PROMPT = """You are a DevOps engineer explaining concepts on X (Twitter) in a single tweet.
Imagine someone in an interview asked you "explain X" — give the most clear, memorable one-liner 
explanation with a practical detail. Pack maximum value into one tweet.

Rules:
- Write ONE tweet that explains a concept clearly. Use a plain English analogy or a real-world 
  comparison to make it stick.
- Include a practical detail, gotcha, or interview tip — not just a definition.
- Sound like a real person. Use contractions, casual language, short sentences.
- NO words like "crucial", "essential", "leverage", "comprehensive", "robust", "utilizing"
- NO "Let's dive in", "Let me explain" — just explain it directly.
- Add 3-5 relevant hashtags at the end.
- Hashtag examples: #DevOps #AWS #Kubernetes #Docker #Terraform #CloudComputing #CICD #SRE
  #Linux #PlatformEngineering #InfraAsCode #GitOps #CloudNative #InterviewTips #TechTwitter
- Tweet MUST be under 270 characters. This is NON-NEGOTIABLE.

Respond ONLY in this exact JSON format, no markdown fences:
{
  "tweet": "the tweet text",
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
                max_tokens=500,
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
    """Use Claude API to generate a single concept tweet."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

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

Pick ONE specific concept and explain it in a single tweet.
STRICT LIMIT: must be under 270 characters. Count carefully."""

    messages = [{"role": "user", "content": user_prompt}]

    for attempt in range(1, MAX_RETRIES + 1):
        message = _call_claude_with_retry(client, SYSTEM_PROMPT, messages)

        response_text = message.content[0].text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        content = json.loads(response_text)

        tweet_len = len(content["tweet"])

        if tweet_len <= MAX_TWEET_LENGTH:
            return content

        print(f"Attempt {attempt}/{MAX_RETRIES}: tweet={tweet_len} chars — retrying...")

        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": message.content[0].text},
            {"role": "user", "content": (
                f"The tweet is {tweet_len} chars. "
                f"It MUST be under {MAX_TWEET_LENGTH} characters. "
                f"Shorten it and respond in the same JSON format."
            )},
        ]

    # Final fallback: truncate
    print("Max retries exceeded — truncating content to fit limits.")
    content["tweet"] = truncate_to_limit(content["tweet"])
    return content


def post_to_x(tweet_text: str) -> dict:
    """Post a single tweet using X API v2."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    tweet = client.create_tweet(text=tweet_text)
    tweet_id = tweet.data["id"]
    print(f"Posted tweet: {tweet_id}")

    return {"tweet_id": tweet_id}


def log_posted_content(content: dict, tweet_ids: dict):
    """Append to history log for dedup and tracking."""
    log_file = Path("concept_history.json")
    history = []
    if log_file.exists():
        history = json.loads(log_file.read_text())

    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "concept": content.get("concept", "unknown"),
        "tweet": content["tweet"],
        "tweet_id": tweet_ids.get("tweet_id"),
        "content_hash": hashlib.md5(content["tweet"].encode()).hexdigest(),
    }
    history.append(entry)
    log_file.write_text(json.dumps(history, indent=2))
    print(f"Logged entry #{len(history)}")


def main():
    concept = get_todays_concept()
    print(f"Today's concept area: {concept}")

    content = generate_content(concept)
    print(f"Generated tweet ({len(content['tweet'])} chars): {content['tweet']}")

    assert len(content["tweet"]) <= MAX_TWEET_LENGTH, f"Tweet too long: {len(content['tweet'])}"

    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN — skipping post to X")
        tweet_ids = {"tweet_id": "dry_run"}
    else:
        tweet_ids = post_to_x(content["tweet"])

    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
