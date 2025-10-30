# Quick Start Guide: GitHub to Notion Sync

This guide will help you quickly set up and run the GitHub to Notion repository sync.

## Step 1: Get Your API Tokens

### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "Notion Sync"
4. Select scopes:
   - For public repos only: `public_repo`
   - For all repos: `repo`
5. Click "Generate token" and copy it immediately (you won't see it again!)

### Notion Integration Token
1. Go to https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Name it "GitHub Repository Sync"
4. Select capabilities: "Insert content"
5. Click "Submit" and copy the "Internal Integration Token"

### Notion Database/Page ID
**Option A: Use existing database**
1. Open your Notion database
2. Look at the URL: `https://www.notion.so/workspace/DATABASE_ID?v=...`
3. The `DATABASE_ID` is the long string of letters and numbers

**Option B: Create new database** (command will do this for you)
1. Create a new Notion page where you want the database
2. Look at the URL: `https://www.notion.so/My-Page-PAGE_ID`
3. The `PAGE_ID` is the long string at the end
4. **Important**: Share the page with your integration:
   - Click "Share" in top-right
   - Click "Invite"
   - Select your integration name
   - Click "Invite"

## Step 2: Set Up Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your tokens:
```bash
# Use your actual tokens here
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxx

# Choose ONE of these:
# Option A: Use existing database
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxx

# Option B: Create new database (uncomment this and comment out DATABASE_ID)
# NOTION_PAGE_ID=xxxxxxxxxxxxxxxxxxxx
```

## Step 3: Run the Sync

### Method 1: Using Environment Variables (Recommended)
```bash
# Load environment variables
source .env  # or use 'export $(cat .env | xargs)'

# Run the sync
python manage.py sync_github_repos_to_notion
```

### Method 2: Using Command-Line Arguments
```bash
python manage.py sync_github_repos_to_notion \
    --github-token YOUR_GITHUB_TOKEN \
    --notion-token YOUR_NOTION_TOKEN \
    --notion-database-id YOUR_DATABASE_ID
```

### Method 3: Using the Helper Script
```bash
# Set environment variables first
export GITHUB_TOKEN=your_token
export NOTION_TOKEN=your_token
export NOTION_DATABASE_ID=your_db_id

# Run the script
./scripts/sync_github_to_notion.sh
```

## Step 4: View Results

After the sync completes:
1. Open Notion
2. Navigate to your database
3. You should see all your GitHub repositories listed!
4. Each repository will have:
   - Basic info (name, description, URL)
   - Metrics (stars, forks, issues)
   - Quality indicators (README, tests, CI/CD, etc.)
   - Overall status (Active, Needs Attention, Inactive, Archived)

## Troubleshooting

### "GitHub token is required" error
- Make sure you've set the `GITHUB_TOKEN` environment variable
- Check that you've copied the entire token (they're long!)

### "Notion database ID is required" error
- Set either `NOTION_DATABASE_ID` or use `--create-database` with `NOTION_PAGE_ID`

### "Permission denied" error (Notion)
- Make sure you've invited your integration to the database/page
- Go to the database → Share → Invite your integration

### "Bad credentials" error (GitHub)
- Your token may be expired or invalid
- Generate a new token with the correct scopes

### Rate limiting
- GitHub: 5,000 requests/hour (plenty for most users)
- Notion: ~3 requests/second
- If you have 100+ repos, the sync may take a few minutes

## What's Next?

### Automate the Sync
Set up a cron job to sync daily:
```bash
# Edit crontab
crontab -e

# Add this line (daily at 2 AM)
0 2 * * * cd /path/to/your-project && /path/to/venv/bin/python manage.py sync_github_repos_to_notion
```

### Customize the Analysis
Edit `sync_github_repos_to_notion.py` to:
- Add more quality checks
- Customize the status determination logic
- Add repository-specific metadata

### Share Your Database
- Make it public or share with your team
- Create filtered views (e.g., "Needs Attention", "Active Projects")
- Add custom properties or formulas

## Need Help?

See the full documentation at [docs/GITHUB_NOTION_SYNC.md](GITHUB_NOTION_SYNC.md) for:
- Detailed API reference
- Advanced usage examples
- Notion database schema
- Security best practices
