"""
Daily AI Terminology & Concept Explainer Bot
Generates and posts a single tweet explaining an AI/ML concept clearly.
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
You break down intimidating AI jargon into plain English in a single tweet. Your audience is 
developers and tech professionals who want to understand AI without a PhD.

Rules:
- Write ONE tweet that explains an AI concept in plain English. Use a relatable analogy or 
  comparison to make it click instantly.
- Include a practical detail or "why it matters" angle — not just a definition.
- You're a real person, not a professor. Casual, direct, opinionated.
- Use contractions. Short sentences. Fragment sentences are fine.
- NO words like "crucial", "essential", "leverage", "comprehensive", "delve", "fascinating"
- NO "Let's break this down", "Here's a thread", "Let me explain" — just explain it.
- Add 3-5 relevant hashtags at the end.
- Hashtag examples: #AI #MachineLearning #LLM #GenAI #ArtificialIntelligence #DeepLearning
  #ChatGPT #NLP #DataScience #MLOps #AIEngineering #TechTwitter #PromptEngineering
- Tweet MUST be under 270 characters. This is NON-NEGOTIABLE.

Respond ONLY in this exact JSON format, no markdown fences:
{
  "tweet": "the tweet text",
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


def generate_content(topic: str) -> dict:
    """Use Claude API to generate a single AI concept tweet."""
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

Pick ONE specific AI concept or term and explain it in a single tweet.
Make it accessible to developers who aren't ML specialists.
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
    log_file = Path("ai_concept_history.json")
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
    topic = get_todays_topic()
    print(f"Today's AI topic area: {topic}")

    content = generate_content(topic)
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
