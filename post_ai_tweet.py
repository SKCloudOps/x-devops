"""
Daily AI Terminology & Concept Explainer Bot
Generates a 4-tweet thread explaining AI/ML concepts clearly.
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
AI_TOPICS = [
    "llm_fundamentals",
    "prompt_engineering",
    "rag_retrieval_augmented_generation",
    "fine_tuning_and_training",
    "embeddings_and_vectors",
    "transformer_architecture",
    "ai_agents_and_tools",
    "machine_learning_basics",
    "neural_network_concepts",
    "natural_language_processing",
    "computer_vision_basics",
    "generative_ai",
    "model_evaluation_metrics",
    "ai_ethics_and_safety",
    "mlops_and_deployment",
    "tokenization_and_context",
    "attention_mechanism",
    "diffusion_models",
    "reinforcement_learning",
    "ai_infrastructure",
]

SYSTEM_PROMPT = """You are an engineer who works with AI/ML daily and explains concepts on X (Twitter).
You break down intimidating AI jargon into plain English. Your audience is developers and tech 
professionals who want to understand AI without a PhD.

Write a 4-tweet thread:
- Tweet 1 (hook): Make the concept feel approachable. Use "everyone's talking about X but most 
  people can't explain it simply" or a relatable analogy. Add 3-5 relevant hashtags.
- Tweet 2 (plain English): Explain it like you're telling a friend at a bar. No math, no jargon. 
  If you must use a technical term, immediately explain it in parentheses.
- Tweet 3 (why it matters): Real-world application. How is this used in ChatGPT, Midjourney, 
  self-driving cars, etc? Make it tangible and relatable.
- Tweet 4 (takeaway): One thing they should remember. A mental model, analogy, or "next time 
  someone asks you about X, just say..." End with 3-5 relevant hashtags.
- Hashtag examples: #AI #MachineLearning #LLM #GenAI #ArtificialIntelligence #DeepLearning
  #ChatGPT #NLP #DataScience #MLOps #AIEngineering #TechTwitter #PromptEngineering

Voice rules:
- You're a real person, not a professor. Casual, direct, opinionated.
- Use contractions. Short sentences. Fragment sentences are fine.
- NO words like "crucial", "essential", "leverage", "comprehensive", "delve", "fascinating"
- NO "Let's break this down", "Here's a thread", "Let me explain" — just start talking
- NO generic CTAs like "What do you think?" or "Follow for more"
- Make complex things feel simple without being condescending
- Each tweet MUST be under 270 characters. This is NON-NEGOTIABLE.

Respond ONLY in this exact JSON format, no markdown fences:
{
  "tweet_1": "hook tweet",
  "tweet_2": "explanation tweet",
  "tweet_3": "real world tweet",
  "tweet_4": "takeaway tweet",
  "concept": "concept name"
}"""


MAX_TWEET_LENGTH = 280
MAX_RETRIES = 3


def get_todays_topic() -> str:
    """Rotate through AI topics based on day of year."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return AI_TOPICS[day_of_year % len(AI_TOPICS)]


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


def generate_content(topic: str) -> dict:
    """Use Claude API to generate a 4-tweet AI concept thread."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    seed_term = random.choice([
        "GPT", "BERT", "transformer", "attention", "token", "embedding",
        "vector database", "RAG", "hallucination", "fine-tuning", "LoRA",
        "prompt", "context window", "temperature", "top-p", "inference",
        "training data", "backpropagation", "gradient descent", "loss function",
        "overfitting", "underfitting", "bias", "weights", "parameters",
        "diffusion", "GAN", "autoencoder", "CNN", "RNN", "LSTM",
        "reinforcement learning", "reward model", "RLHF", "chain of thought",
        "few-shot", "zero-shot", "multimodal", "vision model", "AGI",
        "AI agent", "tool use", "function calling", "semantic search",
    ])

    user_prompt = f"""AI topic area: {topic}
Seed term (use as inspiration): {seed_term}
Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

Pick ONE specific AI concept or term and explain it in a 4-tweet thread.
Make it accessible to developers who aren't ML specialists.
STRICT LIMIT: every tweet must be under 270 characters. Count carefully."""

    messages = [{"role": "user", "content": user_prompt}]
    tweet_keys = ["tweet_1", "tweet_2", "tweet_3", "tweet_4"]

    for attempt in range(1, MAX_RETRIES + 1):
        message = _call_claude_with_retry(client, SYSTEM_PROMPT, messages)

        response_text = message.content[0].text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        content = json.loads(response_text)

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

    first = client.create_tweet(text=tweets[0])
    first_id = first.data["id"]
    tweet_ids.append(first_id)
    print(f"Posted tweet 1/4: {first_id}")

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
    log_file = Path("ai_concept_history.json")
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
    topic = get_todays_topic()
    print(f"Today's AI topic area: {topic}")

    content = generate_content(topic)
    tweet_keys = ["tweet_1", "tweet_2", "tweet_3", "tweet_4"]
    for key in tweet_keys:
        print(f"{key} ({len(content[key])} chars): {content[key]}")

    for key in tweet_keys:
        assert len(content[key]) <= MAX_TWEET_LENGTH, f"{key} too long: {len(content[key])}"

    tweets = [content[key] for key in tweet_keys]

    if os.environ.get("DRY_RUN", "false").lower() == "true":
        print("DRY RUN — skipping post to X")
        tweet_ids = {"tweet_ids": ["dry_run"] * 4}
    else:
        tweet_ids = post_thread(tweets)

    log_posted_content(content, tweet_ids)
    print("Done!")


if __name__ == "__main__":
    main()
