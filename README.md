# Daily DevOps Tweet Bot 🐦

Automated daily X (Twitter) posts covering Cloud, DevOps, and Platform Engineering — interview questions, trending topics, and architecture insights.

Powered by **Claude API** for content generation and **GitHub Actions** for scheduling.

## How It Works

```
┌─────────────────┐     ┌───────────┐     ┌─────────┐
│ GitHub Actions   │────▶│ Claude API│────▶│  X API  │
│ (cron: 8AM CST) │     │ (generate)│     │ (post)  │
└─────────────────┘     └───────────┘     └─────────┘
         │                                      │
         └──── tweet_history.json ◀─────────────┘
```

1. GitHub Actions triggers daily at **8:00 AM CST**
2. Picks a category (AWS, K8s, CI/CD, Platform Eng, Terraform, SRE, etc.)
3. Calls **Claude Sonnet** to generate a tweet + threaded reply (both < 280 chars)
4. Posts to X as a thread via **tweepy**
5. Commits the content to `tweet_history.json` for tracking

## Content Categories (10-day rotation)

| Day | Category |
|-----|----------|
| 1 | AWS Interview Question |
| 2 | Kubernetes Interview Question |
| 3 | CI/CD Interview Question |
| 4 | Platform Engineering Interview Question |
| 5 | Terraform/IaC Interview Question |
| 6 | DevOps Trending Topic |
| 7 | Cloud Architecture Pattern |
| 8 | SRE/Observability Question |
| 9 | Networking/Security Question |
| 10 | Container Orchestration Question |

## Setup

### 1. Create an X Developer Account

1. Go to [developer.x.com](https://developer.x.com)
2. Create a project and app
3. Set app permissions to **Read and Write**
4. Generate these credentials:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret

### 2. Create the GitHub Repository

```bash
# Create repo under SKCloudOps org
gh repo create SKCloudOps/daily-devops-tweets --private --clone
cd daily-devops-tweets

# Copy all files from this project into the repo
cp -r /path/to/these/files/* .

git add .
git commit -m "Initial commit: daily devops tweet bot"
git push
```

### 3. Add Repository Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `X_API_KEY` | X API Key (Consumer Key) |
| `X_API_SECRET` | X API Secret (Consumer Secret) |
| `X_ACCESS_TOKEN` | X Access Token |
| `X_ACCESS_TOKEN_SECRET` | X Access Token Secret |

### 4. Enable the Workflow

The workflow runs automatically on the cron schedule. To test first:

1. Go to **Actions** tab in your repo
2. Select **Daily DevOps Tweet**
3. Click **Run workflow**
4. Set `dry_run` to `true` for a test (generates but doesn't post)

## Manual Test (Local)

```bash
# Install deps
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export X_API_KEY="..."
export X_API_SECRET="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_TOKEN_SECRET="..."

# Dry run (no post to X)
DRY_RUN=true python post_daily_tweet.py

# Live run
python post_daily_tweet.py
```

## Customization

### Change posting time
Edit the cron in `.github/workflows/daily-tweet.yml`:
```yaml
- cron: '0 14 * * *'  # 14:00 UTC = 8:00 AM CST
```

### Add/modify categories
Edit the `CATEGORIES` list in `post_daily_tweet.py`.

### Adjust tone/style
Edit the `SYSTEM_PROMPT` in `post_daily_tweet.py`.

### Add more seed keywords
Edit the `seed_word` list in the `generate_content()` function.

## Cost

- **Claude API**: ~$0.01-0.02/day (one Sonnet call with ~500 tokens)
- **GitHub Actions**: Free tier covers this easily (< 1 min/run)
- **X API**: Free tier supports 1,500 tweets/month

**Monthly total: ~$0.50**

## License

MIT
