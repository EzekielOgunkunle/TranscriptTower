"""
Django management command to sync GitHub repositories to Notion.

This command fetches all repositories from a GitHub user account,
analyzes their implementation status (tests, CI/CD, README, etc.),
and creates/updates a Notion database page with the status of all repositories.

Usage:
    python manage.py sync_github_repos_to_notion --github-token YOUR_TOKEN --notion-token YOUR_TOKEN --notion-database-id YOUR_DB_ID

Environment Variables (alternative to CLI args):
    GITHUB_TOKEN: Personal access token for GitHub API
    NOTION_TOKEN: Integration token for Notion API
    NOTION_DATABASE_ID: Database ID where repository status will be stored
"""

import os
import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from github import Github, GithubException
from notion_client import Client as NotionClient
import requests

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync GitHub repositories to Notion - analyze all repos and create a status page'

    def add_arguments(self, parser):
        parser.add_argument(
            '--github-token',
            type=str,
            help='GitHub personal access token (or set GITHUB_TOKEN env var)',
        )
        parser.add_argument(
            '--github-username',
            type=str,
            help='GitHub username to fetch repos from (defaults to authenticated user)',
        )
        parser.add_argument(
            '--notion-token',
            type=str,
            help='Notion integration token (or set NOTION_TOKEN env var)',
        )
        parser.add_argument(
            '--notion-database-id',
            type=str,
            help='Notion database ID to store repo status (or set NOTION_DATABASE_ID env var)',
        )
        parser.add_argument(
            '--create-database',
            action='store_true',
            help='Create a new Notion database if database-id is not provided',
        )
        parser.add_argument(
            '--notion-page-id',
            type=str,
            help='Parent Notion page ID (required if --create-database is used)',
        )

    def handle(self, *args, **options):
        """Main entry point for the command."""
        # Get tokens from options or environment
        github_token = options.get('github_token') or os.environ.get('GITHUB_TOKEN')
        notion_token = options.get('notion_token') or os.environ.get('NOTION_TOKEN')
        notion_db_id = options.get('notion_database_id') or os.environ.get('NOTION_DATABASE_ID')
        github_username = options.get('github_username')
        create_database = options.get('create_database', False)
        notion_page_id = options.get('notion_page_id') or os.environ.get('NOTION_PAGE_ID')

        # Validate required parameters
        if not github_token:
            raise CommandError(
                'GitHub token is required. Provide --github-token or set GITHUB_TOKEN environment variable.'
            )
        if not notion_token:
            raise CommandError(
                'Notion token is required. Provide --notion-token or set NOTION_TOKEN environment variable.'
            )
        
        if create_database:
            if not notion_page_id:
                raise CommandError(
                    'Parent page ID is required when creating a new database. '
                    'Provide --notion-page-id or set NOTION_PAGE_ID environment variable.'
                )
        else:
            if not notion_db_id:
                raise CommandError(
                    'Notion database ID is required. Provide --notion-database-id, '
                    'set NOTION_DATABASE_ID environment variable, or use --create-database.'
                )

        self.stdout.write(self.style.SUCCESS('Starting GitHub to Notion sync...'))

        try:
            # Initialize GitHub client
            github_client = Github(github_token)
            
            # Get authenticated user or specified user
            if github_username:
                github_user = github_client.get_user(github_username)
            else:
                github_user = github_client.get_user()
            
            self.stdout.write(f'Fetching repositories for user: {github_user.login}')

            # Initialize Notion client
            notion = NotionClient(auth=notion_token)

            # Create database if needed
            if create_database:
                notion_db_id = self._create_notion_database(notion, notion_page_id)
                self.stdout.write(self.style.SUCCESS(f'Created Notion database: {notion_db_id}'))

            # Fetch all repositories
            repos = list(github_user.get_repos())
            self.stdout.write(f'Found {len(repos)} repositories')

            # Analyze each repository and sync to Notion
            success_count = 0
            for repo in repos:
                try:
                    self.stdout.write(f'Analyzing repository: {repo.full_name}')
                    repo_status = self._analyze_repository(repo)
                    self._sync_to_notion(notion, notion_db_id, repo_status)
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to process {repo.full_name}: {str(e)}')
                    )
                    logger.exception(f'Error processing repository {repo.full_name}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully synced {success_count}/{len(repos)} repositories to Notion'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(f'View your Notion database: https://notion.so/{notion_db_id}')
            )

        except GithubException as e:
            raise CommandError(f'GitHub API error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Unexpected error: {str(e)}')

    def _create_notion_database(self, notion, parent_page_id):
        """Create a new Notion database for repository status."""
        database = notion.databases.create(
            parent={
                "type": "page_id",
                "page_id": parent_page_id
            },
            title=[
                {
                    "type": "text",
                    "text": {
                        "content": "GitHub Repository Status"
                    }
                }
            ],
            properties={
                "Name": {"title": {}},
                "Full Name": {"rich_text": {}},
                "Description": {"rich_text": {}},
                "URL": {"url": {}},
                "Language": {"select": {}},
                "Stars": {"number": {}},
                "Forks": {"number": {}},
                "Open Issues": {"number": {}},
                "Has README": {"checkbox": {}},
                "Has Tests": {"checkbox": {}},
                "Has CI/CD": {"checkbox": {}},
                "Has License": {"checkbox": {}},
                "Has .gitignore": {"checkbox": {}},
                "Last Updated": {"date": {}},
                "Created At": {"date": {}},
                "Is Private": {"checkbox": {}},
                "Is Fork": {"checkbox": {}},
                "Is Archived": {"checkbox": {}},
                "Default Branch": {"rich_text": {}},
                "Size (KB)": {"number": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Active", "color": "green"},
                            {"name": "Needs Attention", "color": "yellow"},
                            {"name": "Inactive", "color": "red"},
                            {"name": "Archived", "color": "gray"}
                        ]
                    }
                },
                "Last Synced": {"date": {}},
            }
        )
        return database['id']

    def _analyze_repository(self, repo):
        """
        Analyze a GitHub repository and extract relevant information.
        
        Args:
            repo: PyGithub Repository object
            
        Returns:
            dict: Repository status information
        """
        # Basic repository information
        status = {
            'name': repo.name,
            'full_name': repo.full_name,
            'description': repo.description or 'No description',
            'url': repo.html_url,
            'language': repo.language or 'Unknown',
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'open_issues': repo.open_issues_count,
            'is_private': repo.private,
            'is_fork': repo.fork,
            'is_archived': repo.archived,
            'default_branch': repo.default_branch,
            'size_kb': repo.size,
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
        }

        # Check for README
        status['has_readme'] = self._check_file_exists(repo, 'README.md') or \
                               self._check_file_exists(repo, 'README.rst') or \
                               self._check_file_exists(repo, 'README.txt')

        # Check for tests (common patterns)
        status['has_tests'] = (
            self._check_directory_exists(repo, 'tests') or
            self._check_directory_exists(repo, 'test') or
            self._check_file_exists(repo, 'pytest.ini') or
            self._check_file_exists(repo, 'tox.ini') or
            self._check_file_exists(repo, 'package.json', content_check='jest') or
            self._check_file_exists(repo, 'package.json', content_check='mocha')
        )

        # Check for CI/CD (GitHub Actions, Travis, CircleCI, etc.)
        status['has_cicd'] = (
            self._check_directory_exists(repo, '.github/workflows') or
            self._check_file_exists(repo, '.travis.yml') or
            self._check_file_exists(repo, '.circleci/config.yml') or
            self._check_file_exists(repo, 'Jenkinsfile') or
            self._check_file_exists(repo, '.gitlab-ci.yml') or
            self._check_file_exists(repo, 'azure-pipelines.yml')
        )

        # Check for license
        status['has_license'] = repo.license is not None or \
                                self._check_file_exists(repo, 'LICENSE') or \
                                self._check_file_exists(repo, 'LICENSE.md')

        # Check for .gitignore
        status['has_gitignore'] = self._check_file_exists(repo, '.gitignore')

        # Determine overall status
        status['overall_status'] = self._determine_status(status)

        return status

    def _check_file_exists(self, repo, file_path, content_check=None):
        """Check if a file exists in the repository."""
        try:
            file_content = repo.get_contents(file_path)
            if content_check and hasattr(file_content, 'decoded_content'):
                # Check if specific content exists in the file
                content = file_content.decoded_content.decode('utf-8', errors='ignore')
                return content_check in content
            return True
        except:
            return False

    def _check_directory_exists(self, repo, dir_path):
        """Check if a directory exists in the repository."""
        try:
            repo.get_contents(dir_path)
            return True
        except:
            return False

    def _determine_status(self, repo_status):
        """Determine overall repository status based on analysis."""
        if repo_status['is_archived']:
            return 'Archived'
        
        # Calculate quality score
        quality_score = 0
        if repo_status['has_readme']:
            quality_score += 1
        if repo_status['has_tests']:
            quality_score += 1
        if repo_status['has_cicd']:
            quality_score += 1
        if repo_status['has_license']:
            quality_score += 1
        if repo_status['has_gitignore']:
            quality_score += 1

        # Determine status based on quality and activity
        if quality_score >= 4:
            return 'Active'
        elif quality_score >= 2:
            return 'Needs Attention'
        else:
            return 'Inactive'

    def _sync_to_notion(self, notion, database_id, repo_status):
        """
        Sync repository status to Notion database.
        
        Args:
            notion: Notion client
            database_id: Notion database ID
            repo_status: Dictionary with repository status
        """
        # Check if repository already exists in Notion
        existing_page = self._find_existing_page(notion, database_id, repo_status['full_name'])
        
        # Prepare properties for Notion
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": repo_status['name'][:100]  # Notion title limit
                        }
                    }
                ]
            },
            "Full Name": {
                "rich_text": [
                    {
                        "text": {
                            "content": repo_status['full_name']
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": repo_status['description'][:2000]  # Limit length
                        }
                    }
                ]
            },
            "URL": {
                "url": repo_status['url']
            },
            "Language": {
                "select": {
                    "name": repo_status['language']
                }
            },
            "Stars": {
                "number": repo_status['stars']
            },
            "Forks": {
                "number": repo_status['forks']
            },
            "Open Issues": {
                "number": repo_status['open_issues']
            },
            "Has README": {
                "checkbox": repo_status['has_readme']
            },
            "Has Tests": {
                "checkbox": repo_status['has_tests']
            },
            "Has CI/CD": {
                "checkbox": repo_status['has_cicd']
            },
            "Has License": {
                "checkbox": repo_status['has_license']
            },
            "Has .gitignore": {
                "checkbox": repo_status['has_gitignore']
            },
            "Is Private": {
                "checkbox": repo_status['is_private']
            },
            "Is Fork": {
                "checkbox": repo_status['is_fork']
            },
            "Is Archived": {
                "checkbox": repo_status['is_archived']
            },
            "Default Branch": {
                "rich_text": [
                    {
                        "text": {
                            "content": repo_status['default_branch']
                        }
                    }
                ]
            },
            "Size (KB)": {
                "number": repo_status['size_kb']
            },
            "Status": {
                "select": {
                    "name": repo_status['overall_status']
                }
            },
            "Last Synced": {
                "date": {
                    "start": datetime.utcnow().isoformat()
                }
            }
        }

        # Add dates if available
        if repo_status['created_at']:
            properties["Created At"] = {
                "date": {
                    "start": repo_status['created_at']
                }
            }
        if repo_status['updated_at']:
            properties["Last Updated"] = {
                "date": {
                    "start": repo_status['updated_at']
                }
            }

        # Create or update page in Notion
        if existing_page:
            notion.pages.update(
                page_id=existing_page['id'],
                properties=properties
            )
        else:
            notion.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )

    def _find_existing_page(self, notion, database_id, full_name):
        """Find existing page in Notion database by repository full name."""
        try:
            results = notion.databases.query(
                database_id=database_id,
                filter={
                    "property": "Full Name",
                    "rich_text": {
                        "equals": full_name
                    }
                }
            )
            if results['results']:
                return results['results'][0]
        except Exception as e:
            logger.warning(f'Failed to query existing page: {str(e)}')
        return None
