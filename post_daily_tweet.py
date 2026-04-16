"""
Daily DevOps/Cloud/Platform Engineering Tweet Bot
Generates and posts a single tweet (interview Q&A) using Claude API and X API v2.
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

# Map categories to Gemini image generation prompts
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

# Unsplash fallback keywords (used when Gemini image generation fails)
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

SYSTEM_PROMPT = """You are a DevOps engineer posting interview questions on X (Twitter).

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
- Write like you're explaining to someone who just started coding
- Contractions are fine: don't, can't, it's, won't
- A little personality is good: "lol", "ngl", "tbh", "this one's tricky"

BANNED WORDS: crucial, essential, leverage, comprehensive, robust, utilizing, fundamental,
ensure, facilitate, optimize, streamline, enhance, implement, In today's, Key takeaway

FORMAT:
The tweet has 2 parts separated by 2 blank lines.

PART 1 — the question (under 260 chars, this is what shows in the feed):
  Start with: Interviewer: "question here"
  Then one line: a short casual reaction. Keep it simple.

PART 2 — the answer (shows after "Show more"):
  Answer in plain simple English. Like explaining to a friend over coffee.
  Real example or tip at the end.
  3-5 hashtags on the last line.

Example of a GOOD tweet:
Interviewer: "What's a load balancer?" — sounds easy but a lot of people overthink it


It just spreads traffic across your servers. Like a waiter who sends customers to empty tables instead of piling everyone at one table.

The trick is: if one server goes down, the load balancer stops sending traffic to it. Your site stays up.

#DevOps #AWS #InterviewTips #CloudComputing

QUESTION STYLE: Ask questions any junior or mid engineer would get in an interview.
Not too hard. Not too easy. The classics.

Respond ONLY in this exact JSON format, no markdown fences.
Use \\n for line breaks in the JSON string:
{
  "tweet": "question part\\n\\n\\nanswer part\\n\\n#hashtags",
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

        try:
            content = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt}/{MAX_RETRIES}: invalid JSON from Claude — {e}")
            if attempt == MAX_RETRIES:
                raise
            continue

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


def generate_gemini_image(category: str) -> str | None:
    """Generate an AI image using Gemini Flash image model (free tier). Returns temp file path or None."""
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
            model="gemini-2.5-flash-preview-04-17",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                ),
            ),
        )

        # Extract image from multimodal response
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    tmp_file.write(part.inline_data.data)
                    tmp_file.close()
                    print(f"Generated Gemini image to {tmp_file.name} (prompt: '{prompt[:60]}...')")
                    return tmp_file.name

        print("Gemini returned no image data")
        return None

    except Exception as e:
        print(f"Failed to generate Gemini image: {e}")
        return None


def fetch_unsplash_image(category: str) -> str | None:
    """Fallback: fetch a stock image from Unsplash. Returns temp file path or None."""
    access_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print("UNSPLASH_ACCESS_KEY not set -- skipping fallback image")
        return None

    keywords = CATEGORY_KEYWORDS.get(category, ["technology", "cloud computing"])
    query = random.choice(keywords)

    try:
        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params={
                "query": query,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {access_key}"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        image_url = data["urls"]["regular"]
        print(f"Fallback: Unsplash image {image_url} (query: '{query}')")

        img_response = requests.get(image_url, timeout=15)
        img_response.raise_for_status()

        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp_file.write(img_response.content)
        tmp_file.close()
        print(f"Downloaded fallback image to {tmp_file.name}")
        return tmp_file.name

    except Exception as e:
        print(f"Unsplash fallback also failed: {e} -- posting without image")
        return None


def post_to_x(tweet_text: str, image_path: str = None) -> dict:
    """Post a tweet (optionally with an image) using X API v2 via tweepy."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    kwargs = {"text": tweet_text}
    image_uploaded = False

    # Upload image if provided
    if image_path:
        try:
            # Media upload requires v1.1 API auth
            auth = tweepy.OAuth1UserHandler(
                os.environ["X_API_KEY"],
                os.environ["X_API_SECRET"],
                os.environ["X_ACCESS_TOKEN"],
                os.environ["X_ACCESS_TOKEN_SECRET"],
            )
            api_v1 = tweepy.API(auth)
            media = api_v1.media_upload(filename=image_path)
            kwargs["media_ids"] = [media.media_id]
            image_uploaded = True
            print(f"Uploaded image, media_id: {media.media_id}")
        except Exception as e:
            print(f"Image upload failed: {e} -- posting without image")
        finally:
            # Clean up temp file
            try:
                os.unlink(image_path)
            except OSError:
                pass

    tweet = client.create_tweet(**kwargs)
    tweet_id = tweet.data["id"]
    post_type = "tweet+image" if image_uploaded else "tweet"
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

    content = generate_content(category)
    print(f"Generated tweet ({len(content['tweet'])} chars): {content['tweet']}")

    assert len(content["tweet"]) <= MAX_TWEET_LENGTH, f"Tweet too long: {len(content['tweet'])}"

    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN -- skipping post to X")
        tweet_ids = {"tweet_id": "dry_run"}
    else:
        # Try Gemini first, fall back to Unsplash
        image_path = generate_gemini_image(category)
        if not image_path:
            print("Gemini failed -- falling back to Unsplash")
            image_path = fetch_unsplash_image(category)
        tweet_ids = post_to_x(content["tweet"], image_path=image_path)

    content["type"] = "qa"

    # Log
    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
