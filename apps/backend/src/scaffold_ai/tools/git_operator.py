"""Tool for Git operations on generated code."""

from pathlib import Path
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError


class GitOperatorTool:
    """Tool for managing Git operations on generated code."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self._repo: Repo | None = None

    @property
    def repo(self) -> Repo:
        """Get or initialize the Git repository."""
        if self._repo is None:
            try:
                self._repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                self._repo = Repo.init(self.repo_path)
        return self._repo

    async def create_branch(self, branch_name: str) -> dict:
        """
        Create a new branch for generated code changes.

        Args:
            branch_name: Name of the branch to create

        Returns:
            dict with success status
        """
        try:
            self.repo.create_head(branch_name)
            self.repo.heads[branch_name].checkout()
            return {"success": True, "branch": branch_name}
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    async def commit_changes(self, message: str, files: list[str]) -> dict:
        """
        Commit generated code changes.

        Args:
            message: Commit message
            files: List of specific files to commit (required)

        Returns:
            dict with success status and commit hash
        """
        if not files:
            return {"success": False, "error": "files parameter is required"}
        
        try:
            self.repo.index.add(files)
            commit = self.repo.index.commit(message)
            return {"success": True, "commit": commit.hexsha}
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    async def get_diff(self) -> str:
        """Get the current diff of uncommitted changes."""
        try:
            return self.repo.git.diff()
        except GitCommandError:
            return ""
