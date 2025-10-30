"""
Tests for the sync_github_repos_to_notion management command.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO


class SyncGithubReposToNotionCommandTest(TestCase):
    """Test the sync_github_repos_to_notion management command."""

    def test_command_requires_github_token(self):
        """Test that command fails without GitHub token."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command(
                'sync_github_repos_to_notion',
                notion_token='test_token',
                notion_database_id='test_db_id',
                stdout=out
            )
        self.assertIn('GitHub token is required', str(cm.exception))

    def test_command_requires_notion_token(self):
        """Test that command fails without Notion token."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command(
                'sync_github_repos_to_notion',
                github_token='test_token',
                notion_database_id='test_db_id',
                stdout=out
            )
        self.assertIn('Notion token is required', str(cm.exception))

    def test_command_requires_notion_database_id_or_create_flag(self):
        """Test that command fails without Notion database ID when not creating."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command(
                'sync_github_repos_to_notion',
                github_token='test_token',
                notion_token='test_token',
                stdout=out
            )
        self.assertIn('Notion database ID is required', str(cm.exception))

    def test_create_database_requires_page_id(self):
        """Test that creating a database requires a parent page ID."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command(
                'sync_github_repos_to_notion',
                github_token='test_token',
                notion_token='test_token',
                create_database=True,
                stdout=out
            )
        self.assertIn('Parent page ID is required', str(cm.exception))

    @patch('transcripts.management.commands.sync_github_repos_to_notion.Github')
    @patch('transcripts.management.commands.sync_github_repos_to_notion.NotionClient')
    def test_command_with_valid_parameters(self, mock_notion, mock_github):
        """Test command execution with valid parameters."""
        # Mock GitHub API
        mock_gh_instance = MagicMock()
        mock_github.return_value = mock_gh_instance
        
        mock_user = MagicMock()
        mock_user.login = 'testuser'
        mock_gh_instance.get_user.return_value = mock_user
        
        # Mock repository
        mock_repo = MagicMock()
        mock_repo.name = 'test-repo'
        mock_repo.full_name = 'testuser/test-repo'
        mock_repo.description = 'Test repository'
        mock_repo.html_url = 'https://github.com/testuser/test-repo'
        mock_repo.language = 'Python'
        mock_repo.stargazers_count = 10
        mock_repo.forks_count = 5
        mock_repo.open_issues_count = 2
        mock_repo.private = False
        mock_repo.fork = False
        mock_repo.archived = False
        mock_repo.default_branch = 'main'
        mock_repo.size = 1024
        mock_repo.created_at = None
        mock_repo.updated_at = None
        mock_repo.license = None
        
        mock_user.get_repos.return_value = [mock_repo]
        
        # Mock Notion API
        mock_notion_instance = MagicMock()
        mock_notion.return_value = mock_notion_instance
        
        mock_notion_instance.databases.query.return_value = {'results': []}
        mock_notion_instance.pages.create.return_value = {'id': 'page_123'}
        
        out = StringIO()
        call_command(
            'sync_github_repos_to_notion',
            github_token='test_github_token',
            notion_token='test_notion_token',
            notion_database_id='test_database_id',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Starting GitHub to Notion sync', output)
        self.assertIn('Fetching repositories for user: testuser', output)
        self.assertIn('Found 1 repositories', output)
        self.assertIn('Successfully synced 1/1 repositories', output)

    @patch('transcripts.management.commands.sync_github_repos_to_notion.Github')
    @patch('transcripts.management.commands.sync_github_repos_to_notion.NotionClient')
    def test_command_handles_github_errors(self, mock_notion, mock_github):
        """Test that command handles GitHub API errors gracefully."""
        from github import GithubException
        
        mock_gh_instance = MagicMock()
        mock_github.return_value = mock_gh_instance
        mock_gh_instance.get_user.side_effect = GithubException(401, 'Bad credentials')
        
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command(
                'sync_github_repos_to_notion',
                github_token='invalid_token',
                notion_token='test_token',
                notion_database_id='test_db_id',
                stdout=out
            )
        self.assertIn('GitHub API error', str(cm.exception))

    @patch('transcripts.management.commands.sync_github_repos_to_notion.Github')
    @patch('transcripts.management.commands.sync_github_repos_to_notion.NotionClient')
    def test_command_creates_database(self, mock_notion, mock_github):
        """Test that command can create a new Notion database."""
        # Mock GitHub
        mock_gh_instance = MagicMock()
        mock_github.return_value = mock_gh_instance
        
        mock_user = MagicMock()
        mock_user.login = 'testuser'
        mock_user.get_repos.return_value = []
        mock_gh_instance.get_user.return_value = mock_user
        
        # Mock Notion
        mock_notion_instance = MagicMock()
        mock_notion.return_value = mock_notion_instance
        mock_notion_instance.databases.create.return_value = {'id': 'new_db_123'}
        
        out = StringIO()
        call_command(
            'sync_github_repos_to_notion',
            github_token='test_github_token',
            notion_token='test_notion_token',
            create_database=True,
            notion_page_id='parent_page_123',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Created Notion database', output)
        self.assertIn('new_db_123', output)
