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

SYSTEM_PROMPT = """You are a DevOps engineer posting tech tips on X (Twitter).

THE MOST IMPORTANT RULE: Write in very simple, plain English.
Grade 8 reading level. Short words. Short sentences. Like texting a friend.

TOO COMPLEX (never write like this):
  "A VPC provides network isolation within cloud infrastructure using CIDR blocks"
  "Helm facilitates declarative application deployment via chart-based templating"

JUST RIGHT (write like this):
  "A VPC is your own private space in AWS. Nothing gets in unless you say so."
  "Helm is like a package manager for Kubernetes. One command to deploy your whole app."

More rules:
- Use short words. "use" not "utilize". "stop" not "terminate". "check" not "validate"
- Max 15 words per sentence
- No jargon without a plain explanation right after
- Write like you're explaining to someone who just started coding
- Contractions are fine: don't, can't, it's, won't
- A little personality is good: "lol", "ngl", "tbh", "honestly"

BANNED WORDS: crucial, essential, leverage, comprehensive, robust, utilizing, fundamental,
ensure, facilitate, optimize, streamline, enhance, implement, In today's, Key takeaway

FORMAT:
The tweet has 2 parts separated by 2 blank lines.

PART 1 — the hook (under 260 chars, this is what shows in the feed):
  One punchy line that makes people want to click "Show more".
  Make them curious or say something slightly surprising.

PART 2 — the explanation (shows after "Show more"):
  Explain in plain simple English. Use a real-world analogy.
  Add a tip or gotcha that people don't usually know.
  3-5 hashtags on the last line.

Example of a GOOD tweet:
Most people using Kubernetes don't actually know what etcd is. And it's literally the most important part.


etcd is just a key-value store where Kubernetes saves everything — all cluster state, all config. If etcd dies, your whole cluster is blind. That's why you always back it up.

#Kubernetes #DevOps #CloudComputing #SRE

Pick ONE concept per tweet. Something an engineer would Google or hear in a meeting.

Respond ONLY in this exact JSON format, no markdown fences.
Use \\n for line breaks in the JSON string:
{
  "tweet": "hook part\\n\\n\\nexplanation part\\n\\n#hashtags",
  "concept": "concept name"
}"""


MAX_TWEET_LENGTH = 2000  # X Premium allows up to 4000, keeping 2000 for readability
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
                max_tokens=1000,
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

Pick ONE specific concept and explain it.
Put a catchy hook in the first 260 characters (visible in feed).
Put the deeper explanation after two blank lines (hidden behind "Show more").
You have X Premium — tweet can be up to 2000 characters."""

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
