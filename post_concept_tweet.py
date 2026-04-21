"""
Daily DevOps/Cloud Concept Explainer Bot
Posts a 2-tweet thread (hook + explanation) using Claude API and X API v2.
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
- Contractions are fine: don't, can't, it's, won't
- A little personality is good: "lol", "ngl", "tbh", "honestly"

BANNED WORDS: crucial, essential, leverage, comprehensive, robust, utilizing, fundamental,
ensure, facilitate, optimize, streamline, enhance, implement, In today's, Key takeaway

FORMAT: You are writing a 2-tweet THREAD. Two separate tweets.

TWEET 1 — THE HOOK (HARD LIMIT: under 280 characters including spaces and newlines):
  Use one of these proven hook patterns:
  a) "Most engineers using [tech] every day don't know this:"
  b) "The [tech] thing nobody tells you about 👇"
  c) "I wish someone told me this about [concept] earlier:"
  d) "Hot take: most [tech] tutorials skip the most important part"
  e) "This is why your [tech] is [slower/buggier/less secure] than it should be:"
  f) "[Surprising/counterintuitive claim]. Here's why 👇"

  The hook MUST:
  - Be UNDER 280 characters (hard limit, it's its own tweet)
  - Spark curiosity or say something slightly surprising
  - Pull people into tweet 2 (use 👇 or "Thread" or leave them wanting more)

TWEET 2 — THE EXPLANATION (up to 2000 characters):
  Explain in plain simple English. Use a real-world analogy.
  Add a tip or gotcha engineers don't usually know.
  REQUIRED: End with a question CTA before the hashtags, for example:
  - "What's your biggest [tech] headache right now? 👇"
  - "Agree? What would you add? Reply below 👇"
  - "What's a [tech] thing YOU wish someone told you earlier? 👇"
  - "Bookmark this. What other [topic] tips would help? 👇"
  Then 3-5 hashtags on the last line.

Respond ONLY in this exact JSON format, no markdown fences.
Use \\n for line breaks in the JSON string:
{
  "hook": "tweet 1 text (UNDER 280 chars)",
  "thread": "tweet 2 text with explanation + CTA + hashtags",
  "concept": "concept name"
}"""


MAX_HOOK_LENGTH = 280
MAX_THREAD_LENGTH = 2000
MAX_RETRIES = 3


def get_todays_concept() -> str:
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return CONCEPTS[day_of_year % len(CONCEPTS)]


def truncate_to_limit(text: str, limit: int) -> str:
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
    for api_attempt in range(1, max_api_retries + 1):
        try:
            return client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
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
Sub-topic inspiration: {seed_keyword}
Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

Write a 2-tweet thread that explains ONE specific concept an engineer would Google or hear in a meeting.

TWEET 1 (hook): Must be UNDER 280 characters. Use a strong hook from the prompt.
TWEET 2 (thread reply): Plain English explanation with a real-world analogy + tip/gotcha. End with a question CTA. Aim for 400-900 chars."""

    messages = [{"role": "user", "content": user_prompt}]

    for attempt in range(1, MAX_RETRIES + 1):
        message = _call_claude_with_retry(client, SYSTEM_PROMPT, messages)

        response_text = message.content[0].text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        try:
            content = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt}/{MAX_RETRIES}: invalid JSON — {e}")
            if attempt == MAX_RETRIES:
                raise
            continue

        hook_len = len(content.get("hook", ""))
        thread_len = len(content.get("thread", ""))

        if hook_len <= MAX_HOOK_LENGTH and thread_len <= MAX_THREAD_LENGTH:
            return content

        print(f"Attempt {attempt}/{MAX_RETRIES}: hook={hook_len} chars, thread={thread_len} chars — retrying...")

        issues = []
        if hook_len > MAX_HOOK_LENGTH:
            issues.append(f"hook is {hook_len} chars (must be under {MAX_HOOK_LENGTH})")
        if thread_len > MAX_THREAD_LENGTH:
            issues.append(f"thread is {thread_len} chars (must be under {MAX_THREAD_LENGTH})")

        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": message.content[0].text},
            {"role": "user", "content": (
                f"Problem: {' and '.join(issues)}. "
                f"Shorten and respond in the same JSON format."
            )},
        ]

    print("Max retries exceeded — truncating to fit limits.")
    content["hook"] = truncate_to_limit(content.get("hook", ""), MAX_HOOK_LENGTH)
    content["thread"] = truncate_to_limit(content.get("thread", ""), MAX_THREAD_LENGTH)
    return content


def post_to_x(hook: str, thread: str) -> dict:
    """Post a 2-tweet thread. Hook is tweet 1; thread reply has the explanation + CTA."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    hook_tweet = client.create_tweet(text=hook)
    hook_id = hook_tweet.data["id"]
    print(f"Posted hook: {hook_id}")

    thread_tweet = client.create_tweet(text=thread, in_reply_to_tweet_id=hook_id)
    thread_id = thread_tweet.data["id"]
    print(f"Posted thread reply: {thread_id}")

    return {"hook_id": hook_id, "thread_id": thread_id}


def log_posted_content(content: dict, tweet_ids: dict):
    log_file = Path("concept_history.json")
    history = []
    if log_file.exists():
        history = json.loads(log_file.read_text())

    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "concept": content.get("concept", "unknown"),
        "hook": content.get("hook", ""),
        "thread": content.get("thread", ""),
        "hook_id": tweet_ids.get("hook_id"),
        "thread_id": tweet_ids.get("thread_id"),
        "content_hash": hashlib.md5(
            (content.get("hook", "") + content.get("thread", "")).encode()
        ).hexdigest(),
    }
    history.append(entry)
    log_file.write_text(json.dumps(history, indent=2))
    print(f"Logged entry #{len(history)}")


def main():
    concept = get_todays_concept()
    print(f"Today's concept area: {concept}")

    content = generate_content(concept)
    hook = content["hook"]
    thread = content["thread"]
    print(f"Hook ({len(hook)} chars): {hook}")
    print(f"Thread ({len(thread)} chars): {thread}")

    assert len(hook) <= MAX_HOOK_LENGTH, f"Hook too long: {len(hook)}"
    assert len(thread) <= MAX_THREAD_LENGTH, f"Thread too long: {len(thread)}"

    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN — skipping post to X")
        tweet_ids = {"hook_id": "dry_run", "thread_id": "dry_run"}
    else:
        tweet_ids = post_to_x(hook, thread)

    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
