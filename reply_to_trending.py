"""
Trending Reply Bot — 70/30 Engagement Strategy
Searches for trending DevOps/Cloud/AI tweets and posts thoughtful replies.

IMPORTANT: Requires X API Basic tier ($100/month) or higher.
The free tier is write-only and does not support tweet search.
Get Basic access at: https://developer.x.com/en/portal/products/basic

Env vars required:
  X_BEARER_TOKEN       — for search (Basic tier)
  X_API_KEY            — for posting replies
  X_API_SECRET
  X_ACCESS_TOKEN
  X_ACCESS_TOKEN_SECRET
  ANTHROPIC_API_KEY    — for reply generation
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

import sys

import anthropic
import tweepy


# --- Configuration ---

# Search queries — each finds recent tweets in our niche
# Ordered from most specific to most broad
SEARCH_QUERIES = [
    '(kubernetes OR k8s) -is:retweet -is:reply lang:en',
    '(terraform OR "infrastructure as code") -is:retweet -is:reply lang:en',
    '("platform engineering" OR "developer platform" OR backstage) -is:retweet -is:reply lang:en',
    '(argocd OR "github actions" OR tekton OR flux) -is:retweet -is:reply lang:en',
    '("aws eks" OR "aws lambda" OR "aws iam" OR "aws vpc") -is:retweet -is:reply lang:en',
    '(devops OR "site reliability engineering" OR sre) -is:retweet -is:reply lang:en',
    '(helm OR cilium OR crossplane OR karpenter) -is:retweet -is:reply lang:en',
]

# Replies per GitHub Actions run — keep low to look natural
MAX_REPLIES_PER_RUN = int(os.environ.get("MAX_REPLIES", "8"))

# Only reply to tweets with at least this many likes (filters out noise)
MIN_LIKES = 5

# Only reply to tweets from accounts with at least this many followers
MIN_AUTHOR_FOLLOWERS = 500

# Skip tweets older than this many hours (stale conversations get no visibility)
MAX_AGE_HOURS = 12

REPLY_HISTORY_FILE = Path("reply_history.json")

REPLY_SYSTEM_PROMPT = """You are a senior DevOps/Platform engineer replying to tweets on X.

YOUR GOAL: Add genuine value that makes people want to follow you.

GOOD REPLIES add ONE of:
- A specific tip from real experience ("This bit me last week — the fix is X")
- A gotcha or edge case they didn't mention ("Worth noting: this breaks if you use Y")
- A concrete real-world example ("We used this pattern in prod. One thing: X")
- A follow-up question that shows you know the topic ("Curious how you handle Z — we hit that edge case")
- A friendly counter-point or alternative ("Interesting — we went with X instead because Y")

BAD REPLIES (never write these):
- "Great post! Very informative 🙌"
- "Thanks for sharing!"
- "Follow me for more DevOps tips!"
- Generic agreement without adding anything
- Anything that sounds like a bot

TONE: Real engineer talking to another engineer. Casual, direct, honest.
Use contractions. A little personality is fine.

LENGTH: Under 260 characters. Short and punchy beats long and thorough.

Respond ONLY with the reply text. No JSON. No quotes. Just the reply itself."""


def load_reply_history() -> set:
    """Returns set of tweet IDs already replied to."""
    if not REPLY_HISTORY_FILE.exists():
        return set()
    history = json.loads(REPLY_HISTORY_FILE.read_text())
    return {entry["original_tweet_id"] for entry in history}


def save_reply(original_tweet_id: str, original_text: str, reply_text: str, reply_tweet_id: str):
    history = []
    if REPLY_HISTORY_FILE.exists():
        history = json.loads(REPLY_HISTORY_FILE.read_text())

    entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "original_tweet_id": original_tweet_id,
        "original_text": original_text[:200],
        "reply_text": reply_text,
        "reply_tweet_id": reply_tweet_id,
        "content_hash": hashlib.md5(reply_text.encode()).hexdigest(),
    }
    history.append(entry)
    REPLY_HISTORY_FILE.write_text(json.dumps(history, indent=2))


def fetch_candidate_tweets(bearer_token: str, already_replied: set, own_user_id: str) -> list[dict]:
    """Search for trending DevOps/Cloud/AI tweets to reply to. Requires Basic tier."""
    search_client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    candidates = []
    seen_ids = set()

    for query in SEARCH_QUERIES:
        try:
            response = search_client.search_recent_tweets(
                query=query,
                max_results=10,
                tweet_fields=["public_metrics", "created_at", "author_id", "text"],
                expansions=["author_id"],
                user_fields=["username", "public_metrics"],
                start_time=cutoff,
            )
        except tweepy.errors.Forbidden as e:
            print(
                f"Search failed: {e}\n"
                "Tweet search requires X API Basic tier or higher.\n"
                "Upgrade at: https://developer.x.com/en/portal/products/basic"
            )
            raise
        except tweepy.errors.TweepyException as e:
            print(f"Search query failed ({query[:40]}...): {e}")
            continue

        if not response.data:
            continue

        # Build author lookup from expansions
        users = {}
        if response.includes and response.includes.get("users"):
            for user in response.includes["users"]:
                users[user.id] = user

        for tweet in response.data:
            tweet_id = str(tweet.id)

            # Skip dupes, own tweets, already-replied
            if tweet_id in seen_ids:
                continue
            if tweet_id in already_replied:
                continue
            if str(tweet.author_id) == own_user_id:
                continue

            seen_ids.add(tweet_id)

            metrics = tweet.public_metrics or {}
            likes = metrics.get("like_count", 0)
            if likes < MIN_LIKES:
                continue

            author = users.get(tweet.author_id)
            if author:
                author_followers = (author.public_metrics or {}).get("followers_count", 0)
                if author_followers < MIN_AUTHOR_FOLLOWERS:
                    continue
                author_username = author.username
            else:
                author_username = "unknown"

            candidates.append({
                "id": tweet_id,
                "text": tweet.text,
                "likes": likes,
                "author_username": author_username,
                "author_followers": author_followers if author else 0,
                "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
            })

    # Sort by likes descending — reply to highest-engagement tweets first
    candidates.sort(key=lambda t: t["likes"], reverse=True)
    return candidates[:MAX_REPLIES_PER_RUN * 2]  # fetch extra in case some fail


def generate_reply(tweet_text: str, author_username: str) -> str:
    """Use Claude to generate a valuable reply to the given tweet."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_prompt = f"""Tweet by @{author_username}:
"{tweet_text}"

Write a reply that adds genuine value. Under 260 characters.
Don't start with "@{author_username}" — X adds the mention automatically."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=REPLY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    reply = message.content[0].text.strip()
    # Strip any quotes Claude might wrap around the reply
    reply = reply.strip('"').strip("'")
    return reply


def post_reply(reply_text: str, tweet_id: str) -> str:
    """Post a reply to the given tweet ID. Returns the reply tweet ID."""
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    response = client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
    return str(response.data["id"])


def get_own_user_id(bearer_token: str) -> str:
    """Fetch the authenticated account's user ID to exclude own tweets from search."""
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    me = client.get_me()
    return str(me.data.id)


def main():
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    if not bearer_token:
        print(
            "X_BEARER_TOKEN not set — skipping reply bot.\n"
            "Tweet search requires X API Basic tier ($100/month).\n"
            "Add X_BEARER_TOKEN to repo secrets once you upgrade:\n"
            "  developer.x.com → Products → Basic"
        )
        sys.exit(0)

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"

    print("Fetching own user ID...")
    own_user_id = get_own_user_id(bearer_token)
    print(f"Own user ID: {own_user_id}")

    already_replied = load_reply_history()
    print(f"Already replied to {len(already_replied)} tweets (skipping those)")

    print("Searching for candidate tweets...")
    candidates = fetch_candidate_tweets(bearer_token, already_replied, own_user_id)
    print(f"Found {len(candidates)} candidates after filtering")

    replies_posted = 0

    for tweet in candidates:
        if replies_posted >= MAX_REPLIES_PER_RUN:
            break

        tweet_id = tweet["id"]
        tweet_text = tweet["text"]
        author = tweet["author_username"]
        likes = tweet["likes"]

        print(f"\n--- Candidate tweet ({likes} likes) by @{author} ---")
        print(f"  {tweet_text[:120]}{'...' if len(tweet_text) > 120 else ''}")

        try:
            reply_text = generate_reply(tweet_text, author)
        except Exception as e:
            print(f"  Claude failed to generate reply: {e}")
            continue

        print(f"  Generated reply ({len(reply_text)} chars): {reply_text}")

        if len(reply_text) > 280:
            print(f"  Reply too long ({len(reply_text)} chars) — skipping")
            continue

        if dry_run:
            print("  DRY RUN — not posting")
            reply_tweet_id = "dry_run"
        else:
            try:
                reply_tweet_id = post_reply(reply_text, tweet_id)
                print(f"  Posted reply: {reply_tweet_id}")
                # Brief pause between replies to avoid looking like a spam bot
                time.sleep(30)
            except tweepy.errors.TweepyException as e:
                print(f"  Failed to post reply: {e}")
                continue

        save_reply(tweet_id, tweet_text, reply_text, reply_tweet_id)
        replies_posted += 1

    print(f"\nDone. Posted {replies_posted} replies.")


if __name__ == "__main__":
    main()
