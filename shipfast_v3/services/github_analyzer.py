"""
GitHub Analyzer Service
Fetches and analyzes GitHub repositories using GitHub REST API
"""

import re
import requests
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger("github_analyzer")


class GitHubAnalyzer:
    """Analyzes GitHub repositories"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub analyzer
        
        Args:
            token: Optional GitHub personal access token for higher rate limits
        """
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def analyze_repository(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Analyze a GitHub repository
        
        Args:
            repo_url: GitHub repository URL (https://github.com/owner/repo)
            branch: Branch name (default: main)
            
        Returns:
            Dictionary with repository analysis
        """
        result = {
            "success": False,
            "repo_info": {},
            "file_structure": {},
            "tech_stack": {},
            "dependencies": {},
        }
        
        try:
            # Parse repository URL
            owner, repo = self._parse_repo_url(repo_url)
            if not owner or not repo:
                result["error"] = "Invalid GitHub URL format"
                return result
            
            # Get repository info
            repo_info = self._get_repo_info(owner, repo)
            if not repo_info:
                result["error"] = "Failed to fetch repository info (404 or private repo)"
                return result
            
            result["repo_info"] = repo_info
            
            # Get repository tree (file structure)
            tree = self._get_repo_tree(owner, repo, branch)
            if not tree and branch == "main":
                # Try master branch
                logger.info("Branch 'main' not found, trying 'master'")
                tree = self._get_repo_tree(owner, repo, "master")
                if tree:
                    branch = "master"
            
            if not tree:
                result["error"] = f"Failed to fetch repository tree for branch '{branch}'"
                return result
            
            result["file_structure"] = tree
            
            # Analyze tech stack
            tech_stack = self._analyze_tech_stack(tree)
            result["tech_stack"] = tech_stack
            
            # Get dependencies
            dependencies = self._get_dependencies(owner, repo, branch, tree)
            result["dependencies"] = dependencies
            
            result["success"] = True
            logger.info(
                "Repository analyzed successfully",
                owner=owner,
                repo=repo,
                branch=branch,
                files=len(tree.get("tree", [])),
            )
            
        except Exception as e:
            logger.error("Repository analysis failed", error=str(e))
            result["error"] = str(e)
        
        return result
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub repository URL to extract owner and repo name"""
        # Strip trailing slashes and whitespace
        repo_url = repo_url.strip().rstrip('/')
        
        # Match patterns like:
        # https://github.com/owner/repo
        # github.com/owner/repo
        # owner/repo
        pattern = r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, repo_url)
        
        if match:
            owner = match.group(1)
            repo = match.group(2).replace(".git", "")
            return owner, repo
        
        # Try simple owner/repo format
        if "/" in repo_url and len(repo_url.split("/")) == 2:
            parts = repo_url.split("/")
            return parts[0], parts[1].replace(".git", "")
        
        return None, None
    
    def _get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository information from GitHub API"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                logger.error("Repository not found (404)", owner=owner, repo=repo)
                return None
            
            if response.status_code != 200:
                logger.error(
                    "Failed to fetch repo info",
                    status_code=response.status_code,
                    owner=owner,
                    repo=repo,
                )
                return None
            
            data = response.json()
            return {
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "language": data.get("language"),
                "default_branch": data.get("default_branch", "main"),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "size": data.get("size", 0),
            }
            
        except Exception as e:
            logger.error("Exception while fetching repo info", error=str(e))
            return None
    
    def _get_repo_tree(self, owner: str, repo: str, branch: str) -> Optional[Dict]:
        """Get repository file tree from GitHub API"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                logger.error(
                    "Repository tree not found (404)",
                    owner=owner,
                    repo=repo,
                    branch=branch,
                )
                return None
            
            if response.status_code != 200:
                logger.error(
                    "Failed to fetch repo tree",
                    status_code=response.status_code,
                    owner=owner,
                    repo=repo,
                    branch=branch,
                )
                return None
            
            return response.json()
            
        except Exception as e:
            logger.error("Exception while fetching repo tree", error=str(e))
            return None
    
    def _analyze_tech_stack(self, tree: Dict) -> Dict[str, Any]:
        """Analyze technology stack from file extensions"""
        tech_stack = {
            "languages": set(),
            "frameworks": set(),
            "databases": set(),
            "build_tools": set(),
        }
        
        files = tree.get("tree", [])
        
        # Language detection
        for file in files:
            path = file.get("path", "")
            
            if path.endswith(".py"):
                tech_stack["languages"].add("Python")
            elif path.endswith((".js", ".jsx")):
                tech_stack["languages"].add("JavaScript")
            elif path.endswith((".ts", ".tsx")):
                tech_stack["languages"].add("TypeScript")
            elif path.endswith(".go"):
                tech_stack["languages"].add("Go")
            elif path.endswith((".java", ".kt")):
                tech_stack["languages"].add("Java/Kotlin")
            elif path.endswith(".rs"):
                tech_stack["languages"].add("Rust")
            
            # Framework detection
            if "requirements.txt" in path or "setup.py" in path:
                tech_stack["frameworks"].add("Python")
            elif "package.json" in path:
                tech_stack["frameworks"].add("Node.js")
            elif "Cargo.toml" in path:
                tech_stack["frameworks"].add("Rust")
            elif "go.mod" in path:
                tech_stack["frameworks"].add("Go")
            
            # Build tools
            if "Dockerfile" in path:
                tech_stack["build_tools"].add("Docker")
            elif "docker-compose" in path:
                tech_stack["build_tools"].add("Docker Compose")
            elif path.endswith(".tf"):
                tech_stack["build_tools"].add("Terraform")
        
        # Convert sets to lists
        return {
            "languages": sorted(list(tech_stack["languages"])),
            "frameworks": sorted(list(tech_stack["frameworks"])),
            "databases": sorted(list(tech_stack["databases"])),
            "build_tools": sorted(list(tech_stack["build_tools"])),
        }
    
    def _get_dependencies(
        self, owner: str, repo: str, branch: str, tree: Dict
    ) -> Dict[str, List[str]]:
        """Extract dependencies from common dependency files"""
        dependencies = {}
        
        files = tree.get("tree", [])
        dependency_files = [
            "requirements.txt",
            "package.json",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
        ]
        
        for file in files:
            path = file.get("path", "")
            
            if any(dep_file in path for dep_file in dependency_files):
                # Fetch file content
                content = self._get_file_content(owner, repo, path, branch)
                if content:
                    dependencies[path] = content[:500]  # First 500 chars
        
        return dependencies
    
    def _get_file_content(
        self, owner: str, repo: str, path: str, branch: str
    ) -> Optional[str]:
        """Get file content from GitHub API"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # GitHub returns base64 encoded content
                import base64
                content = base64.b64decode(data.get("content", "")).decode("utf-8")
                return content
            
        except Exception as e:
            logger.error("Failed to fetch file content", path=path, error=str(e))
        
        return None
