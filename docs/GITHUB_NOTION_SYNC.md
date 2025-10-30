# GitHub to Notion Repository Sync

This Django management command allows you to automatically sync all your GitHub repositories to a Notion database, providing a comprehensive overview of your repository portfolio.

## Features

The command analyzes each repository and tracks:

- **Basic Information**: Name, description, URL, language
- **Metrics**: Stars, forks, open issues, size
- **Quality Indicators**:
  - Has README
  - Has tests (detects common test directories and configurations)
  - Has CI/CD (GitHub Actions, Travis CI, CircleCI, Jenkins, GitLab CI, Azure Pipelines)
  - Has license
  - Has .gitignore
- **Status**: Active, Needs Attention, Inactive, or Archived
- **Metadata**: Created date, last updated, private/public, fork status

## Prerequisites

1. **GitHub Personal Access Token**: Create one at https://github.com/settings/tokens
   - Required scope: `repo` (for private repos) or `public_repo` (for public repos only)

2. **Notion Integration Token**: Create an integration at https://www.notion.so/my-integrations
   - Required capability: Insert content

3. **Notion Database or Page ID**:
   - Option A: Use an existing database (provide `--notion-database-id`)
   - Option B: Create a new database (provide `--notion-page-id` and use `--create-database`)

## Installation

The required packages are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Using Command-Line Arguments

```bash
python manage.py sync_github_repos_to_notion \
    --github-token YOUR_GITHUB_TOKEN \
    --notion-token YOUR_NOTION_TOKEN \
    --notion-database-id YOUR_DATABASE_ID
```

### Method 2: Using Environment Variables (Recommended for Security)

```bash
export GITHUB_TOKEN=your_github_token_here
export NOTION_TOKEN=your_notion_token_here
export NOTION_DATABASE_ID=your_database_id_here

python manage.py sync_github_repos_to_notion
```

### Method 3: Create a New Notion Database

```bash
python manage.py sync_github_repos_to_notion \
    --github-token YOUR_GITHUB_TOKEN \
    --notion-token YOUR_NOTION_TOKEN \
    --create-database \
    --notion-page-id YOUR_PARENT_PAGE_ID
```

### Sync Specific User's Repositories

By default, the command syncs repositories for the authenticated user. To sync another user's public repositories:

```bash
python manage.py sync_github_repos_to_notion \
    --github-token YOUR_GITHUB_TOKEN \
    --github-username TARGET_USERNAME \
    --notion-token YOUR_NOTION_TOKEN \
    --notion-database-id YOUR_DATABASE_ID
```

## How It Works

1. **Authentication**: Connects to GitHub and Notion APIs using provided tokens
2. **Repository Fetching**: Retrieves all repositories for the specified GitHub user
3. **Analysis**: For each repository, checks for:
   - README files (README.md, README.rst, README.txt)
   - Test directories (tests/, test/) and test configuration files
   - CI/CD configurations (.github/workflows/, .travis.yml, etc.)
   - License files
   - .gitignore file
4. **Status Determination**: 
   - **Active**: 4-5 quality indicators present
   - **Needs Attention**: 2-3 quality indicators present
   - **Inactive**: 0-1 quality indicators present
   - **Archived**: Repository is archived on GitHub
5. **Notion Sync**: Creates or updates pages in the Notion database

## Notion Database Schema

The command creates a database with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Repository name |
| Full Name | Text | Full repository name (owner/repo) |
| Description | Text | Repository description |
| URL | URL | GitHub repository URL |
| Language | Select | Primary programming language |
| Stars | Number | Number of stars |
| Forks | Number | Number of forks |
| Open Issues | Number | Number of open issues |
| Has README | Checkbox | README file exists |
| Has Tests | Checkbox | Test files/directories exist |
| Has CI/CD | Checkbox | CI/CD configuration exists |
| Has License | Checkbox | License file exists |
| Has .gitignore | Checkbox | .gitignore file exists |
| Last Updated | Date | Last repository update |
| Created At | Date | Repository creation date |
| Is Private | Checkbox | Private repository flag |
| Is Fork | Checkbox | Fork repository flag |
| Is Archived | Checkbox | Archived repository flag |
| Default Branch | Text | Default branch name |
| Size (KB) | Number | Repository size in KB |
| Status | Select | Overall status (Active/Needs Attention/Inactive/Archived) |
| Last Synced | Date | Last sync timestamp |

## Examples

### Basic Sync

```bash
# Set environment variables in your shell profile or .env file
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export NOTION_TOKEN=secret_xxxxxxxxxxxx
export NOTION_DATABASE_ID=xxxxxxxxxxxx

# Run the sync
python manage.py sync_github_repos_to_notion
```

### Sync with Verbose Output

```bash
python manage.py sync_github_repos_to_notion -v 2
```

### Create New Database and Sync

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export NOTION_TOKEN=secret_xxxxxxxxxxxx
export NOTION_PAGE_ID=xxxxxxxxxxxx

python manage.py sync_github_repos_to_notion --create-database
```

## Automation

You can automate this sync using cron (Linux/Mac) or Task Scheduler (Windows):

### Using Cron (Daily at 2 AM)

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed)
0 2 * * * cd /path/to/TranscriptTower && /path/to/venv/bin/python manage.py sync_github_repos_to_notion
```

### Using Django Management Command in Background

```bash
# Run as a background job
nohup python manage.py sync_github_repos_to_notion > /tmp/github_notion_sync.log 2>&1 &
```

## Troubleshooting

### "GitHub token is required" Error
Ensure you've provided the token via `--github-token` or `GITHUB_TOKEN` environment variable.

### "Notion database ID is required" Error
Either provide `--notion-database-id` or use `--create-database` with `--notion-page-id`.

### Rate Limiting
- GitHub: 5,000 requests/hour for authenticated requests
- Notion: ~3 requests/second

If you have many repositories, the sync may take time. The command handles rate limits gracefully.

### Permission Errors (Notion)
Ensure your Notion integration has been invited to the database or parent page.

### Permission Errors (GitHub)
Ensure your GitHub token has the appropriate scopes (`repo` or `public_repo`).

## Security Best Practices

1. **Never commit tokens** to version control
2. Use environment variables for sensitive data
3. Rotate tokens regularly
4. Use minimal required scopes for tokens
5. Consider using a secrets manager for production deployments

## Future Enhancements

Potential future additions:
- Support for filtering repositories by criteria
- Additional analysis metrics (code quality, security alerts)
- Webhook integration for real-time updates
- Batch processing for large repository counts
- Custom status rules configuration

## Support

For issues or questions, please open an issue on the GitHub repository.
