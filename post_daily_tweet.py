"""
Daily DevOps/Cloud/Platform Engineering Tweet Bot
Posts a 2-tweet thread (hook + answer) using Claude API and X API v2.
"""

import os
import json
import random
import hashlib
import time
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import requests
import tweepy
from google import genai
from google.genai import types


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

CATEGORY_IMAGE_PROMPTS = {
    "aws_interview_question": [
        "A sleek futuristic cloud data center with glowing blue AWS-style server racks, dark background, tech aesthetic",
        "Abstract cloud computing visualization with interconnected nodes and orange-blue gradient, modern tech art",
    ],
    "kubernetes_interview_question": [
        "A stylized container ship made of glowing blue containers connected by network lines, dark tech background",
        "Abstract Kubernetes cluster visualization with pods and nodes as glowing hexagons, cyberpunk aesthetic",
    ],
    "cicd_interview_question": [
        "A futuristic CI/CD pipeline visualization with glowing stages flowing left to right, neon blue and green, dark background",
        "Abstract software deployment pipeline with automated gears and code streams, modern tech illustration",
    ],
    "platform_engineering_interview_question": [
        "A futuristic platform engineering dashboard with holographic infrastructure layers, dark mode tech aesthetic",
        "Abstract developer platform with interconnected tools and services as glowing nodes, modern tech art",
    ],
    "terraform_iac_interview_question": [
        "Infrastructure as code visualization with glowing terraform-style resource blocks connected by lines, dark tech background",
        "Abstract cloud infrastructure blueprint with geometric shapes and code overlays, futuristic tech art",
    ],
    "devops_trending_topic": [
        "A futuristic DevOps infinity loop symbol made of glowing circuit lines, dark background, neon blue and purple",
        "Abstract DevOps workflow with automated processes and collaboration symbols, modern tech illustration",
    ],
    "cloud_architecture_pattern": [
        "A stunning multi-cloud architecture diagram with glowing connections between AWS, Azure, and GCP nodes, dark tech background",
        "Abstract cloud architecture with layered services as floating holographic panels, futuristic tech art",
    ],
    "sre_observability_question": [
        "A futuristic monitoring dashboard with real-time metrics, graphs, and alerts glowing in green and amber, dark background",
        "Abstract observability visualization with traces, metrics, and logs as flowing data streams, tech aesthetic",
    ],
    "networking_security_question": [
        "A futuristic cybersecurity shield with network topology and firewall layers, glowing blue and red, dark background",
        "Abstract network security visualization with encrypted data flows and lock symbols, cyberpunk tech art",
    ],
    "container_orchestration_question": [
        "Futuristic container orchestration with glowing Docker containers being managed by automated systems, dark tech background",
        "Abstract container cluster with pods scaling up and down as holographic elements, modern tech illustration",
    ],
}

CATEGORY_KEYWORDS = {
    "aws_interview_question": ["cloud computing", "server room", "data center"],
    "kubernetes_interview_question": ["container ship", "server cluster", "technology infrastructure"],
    "cicd_interview_question": ["software development", "coding", "pipeline"],
    "platform_engineering_interview_question": ["engineering", "cloud infrastructure", "technology"],
    "terraform_iac_interview_question": ["infrastructure", "cloud architecture", "coding setup"],
    "devops_trending_topic": ["devops", "technology", "software engineering"],
    "cloud_architecture_pattern": ["cloud computing", "network architecture", "data center"],
    "sre_observability_question": ["monitoring", "dashboard", "analytics"],
    "networking_security_question": ["cybersecurity", "network", "firewall"],
    "container_orchestration_question": ["containers", "docker", "server rack"],
}

SYSTEM_PROMPT = """You are a DevOps engineer posting interview content on X (Twitter).

THE MOST IMPORTANT RULE: Write in very simple, plain English.
Grade 8 reading level. Short words. Short sentences. Like texting a friend.

TOO COMPLEX (never write like this):
  "Containers leverage kernel namespaces to provide process isolation"
  "Kubernetes orchestrates containerized workloads across a distributed cluster"

JUST RIGHT (write like this):
  "A container is just your app + everything it needs, packed in a box"
  "Kubernetes keeps your containers running. If one crashes, it starts a new one"

More rules:
- Use short words. "use" not "utilize". "stop" not "terminate". "check" not "validate"
- Max 15 words per sentence
- No jargon without a plain explanation right after
- Contractions are fine: don't, can't, it's, won't
- A little personality is good: "lol", "ngl", "tbh", "this one's tricky"

BANNED WORDS: crucial, essential, leverage, comprehensive, robust, utilizing, fundamental,
ensure, facilitate, optimize, streamline, enhance, implement, In today's, Key takeaway

FORMAT: You are writing a 2-tweet THREAD. Two separate tweets.

TWEET 1 — THE HOOK (HARD LIMIT: under 280 characters including spaces and newlines):
  Use one of these proven hook patterns — pick whichever fits the topic best:
  a) "Interviewer: '[question]?' — [one punchy observation]"
     e.g., "Interviewer: 'What's a pod disruption budget?' — Most candidates blank here. Would you? 👇"
  b) "This [topic] question trips up most engineers. What's your answer? 👇"
  c) "Got asked this in my last DevOps interview. Be honest — how would YOU answer? 👇"
  d) "[surprising fact or common mistake]. Here's what most engineers miss: 👇"
  e) "3 out of 5 candidates fail this [topic] question. Thread 👇"

  The hook MUST:
  - Be UNDER 280 characters (count carefully — this is a hard limit, it's its own tweet)
  - End with something that makes people want to read tweet 2 (👇 or "Thread" or a cliffhanger)
  - Create urgency, curiosity, or a challenge

TWEET 2 — THE ANSWER (up to 2000 characters):
  Answer the question in plain simple English with a real example or tip.
  REQUIRED: End with a question CTA before the hashtags to drive replies, for example:
  - "What's the trickiest [topic] question you've been asked? Drop it below 👇"
  - "Agree? Or would you answer differently? Reply below 👇"
  - "Got a better answer? I want to hear it 👇"
  - "What else would you add? 👇"
  Then 3-5 hashtags on the last line.

Respond ONLY in this exact JSON format, no markdown fences.
Use \\n for line breaks in the JSON string:
{
  "hook": "tweet 1 text (UNDER 280 chars)",
  "thread": "tweet 2 text with answer + CTA + hashtags",
  "category": "category label"
}"""


def get_todays_category() -> str:
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return CATEGORIES[day_of_year % len(CATEGORIES)]


MAX_HOOK_LENGTH = 280
MAX_THREAD_LENGTH = 2000
MAX_RETRIES = 3


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


def generate_content(category: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

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
Seed keyword (use as inspiration, don't force it): {seed_word}
Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

Write a 2-tweet thread about a FREQUENTLY ASKED interview question.
The kind engineers prep for the night before an interview.

TWEET 1 (hook): Must be UNDER 280 characters. Use a strong hook pattern from the prompt.
TWEET 2 (thread reply): The answer with a real tip or example. End with a question CTA. Aim for 400-900 chars."""

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


def generate_gemini_image(category: str) -> str | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set -- skipping image")
        return None

    prompts = CATEGORY_IMAGE_PROMPTS.get(category, [
        "A futuristic cloud computing visualization with glowing nodes and connections, dark tech background",
    ])
    prompt = random.choice(prompts)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                ),
            ),
        )

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    tmp_file.write(part.inline_data.data)
                    tmp_file.close()
                    print(f"Generated Gemini image (prompt: '{prompt[:60]}...')")
                    return tmp_file.name

        print("Gemini returned no image data")
        return None

    except Exception as e:
        print(f"Failed to generate Gemini image: {e}")
        return None


def fetch_unsplash_image(category: str) -> str | None:
    access_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print("UNSPLASH_ACCESS_KEY not set -- skipping fallback image")
        return None

    keywords = CATEGORY_KEYWORDS.get(category, ["technology", "cloud computing"])
    query = random.choice(keywords)

    try:
        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query, "orientation": "landscape", "content_filter": "high"},
            headers={"Authorization": f"Client-ID {access_key}"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        image_url = data["urls"]["regular"]
        img_response = requests.get(image_url, timeout=15)
        img_response.raise_for_status()

        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp_file.write(img_response.content)
        tmp_file.close()
        print(f"Unsplash fallback image downloaded (query: '{query}')")
        return tmp_file.name

    except Exception as e:
        print(f"Unsplash fallback failed: {e} -- posting without image")
        return None


def post_to_x(hook: str, thread: str, image_path: str = None) -> dict:
    """Post a 2-tweet thread. Hook gets the image; thread reply has the answer + CTA."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    hook_kwargs = {"text": hook}
    image_uploaded = False

    if image_path:
        try:
            auth = tweepy.OAuth1UserHandler(
                os.environ["X_API_KEY"],
                os.environ["X_API_SECRET"],
                os.environ["X_ACCESS_TOKEN"],
                os.environ["X_ACCESS_TOKEN_SECRET"],
            )
            api_v1 = tweepy.API(auth)
            media = api_v1.media_upload(filename=image_path)
            hook_kwargs["media_ids"] = [media.media_id]
            image_uploaded = True
            print(f"Uploaded image, media_id: {media.media_id}")
        except Exception as e:
            print(f"Image upload failed: {e} -- posting hook without image")
        finally:
            try:
                os.unlink(image_path)
            except OSError:
                pass

    hook_tweet = client.create_tweet(**hook_kwargs)
    hook_id = hook_tweet.data["id"]
    print(f"Posted hook {'+ image' if image_uploaded else ''}: {hook_id}")

    thread_tweet = client.create_tweet(text=thread, in_reply_to_tweet_id=hook_id)
    thread_id = thread_tweet.data["id"]
    print(f"Posted thread reply: {thread_id}")

    return {"hook_id": hook_id, "thread_id": thread_id}


def log_posted_content(content: dict, tweet_ids: dict):
    log_file = Path("tweet_history.json")
    history = []
    if log_file.exists():
        history = json.loads(log_file.read_text())

    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "category": content.get("category", "unknown"),
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
    category = get_todays_category()
    print(f"Today's category: {category}")

    content = generate_content(category)
    hook = content["hook"]
    thread = content["thread"]
    print(f"Hook ({len(hook)} chars): {hook}")
    print(f"Thread ({len(thread)} chars): {thread}")

    assert len(hook) <= MAX_HOOK_LENGTH, f"Hook too long: {len(hook)}"
    assert len(thread) <= MAX_THREAD_LENGTH, f"Thread too long: {len(thread)}"

    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN -- skipping post to X")
        tweet_ids = {"hook_id": "dry_run", "thread_id": "dry_run"}
    else:
        image_path = generate_gemini_image(category)
        if not image_path:
            print("Gemini failed -- falling back to Unsplash")
            image_path = fetch_unsplash_image(category)
        tweet_ids = post_to_x(hook, thread, image_path=image_path)

    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
