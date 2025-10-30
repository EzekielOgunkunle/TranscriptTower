#!/bin/bash
# Example script to sync GitHub repositories to Notion
# This script demonstrates how to use the sync_github_repos_to_notion command

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}GitHub to Notion Repository Sync${NC}"
echo "===================================="
echo ""

# Check if required environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}Error: GITHUB_TOKEN environment variable is not set${NC}"
    echo "Please set it with: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

if [ -z "$NOTION_TOKEN" ]; then
    echo -e "${RED}Error: NOTION_TOKEN environment variable is not set${NC}"
    echo "Please set it with: export NOTION_TOKEN=your_token_here"
    exit 1
fi

# Check if database ID or page ID is set
if [ -z "$NOTION_DATABASE_ID" ] && [ -z "$NOTION_PAGE_ID" ]; then
    echo -e "${RED}Error: Either NOTION_DATABASE_ID or NOTION_PAGE_ID must be set${NC}"
    echo "For existing database: export NOTION_DATABASE_ID=your_db_id"
    echo "For new database: export NOTION_PAGE_ID=your_page_id"
    exit 1
fi

echo -e "${YELLOW}Configuration:${NC}"
echo "GitHub Token: ${GITHUB_TOKEN:0:10}..." 
echo "Notion Token: ${NOTION_TOKEN:0:10}..."

if [ -n "$NOTION_DATABASE_ID" ]; then
    echo "Notion Database ID: $NOTION_DATABASE_ID"
    echo ""
    echo -e "${GREEN}Starting sync to existing database...${NC}"
    python manage.py sync_github_repos_to_notion
elif [ -n "$NOTION_PAGE_ID" ]; then
    echo "Notion Page ID: $NOTION_PAGE_ID"
    echo ""
    echo -e "${GREEN}Creating new database and starting sync...${NC}"
    python manage.py sync_github_repos_to_notion --create-database
fi

echo ""
echo -e "${GREEN}Sync completed successfully!${NC}"
