"""ShipFast v3.0 - Code Analyzer Agent

Analyzes codebase to understand:
- Project structure and dependencies (GitHub API integration)
- Tech stack and frameworks (from file types and folders)
- Entry points and services
- Resource requirements
- Docker deployment recommendations
"""

from typing import Dict, Any, List
import json
import os
from pathlib import Path
from agents.base import BaseAgent
from core.state import WorkflowState
from services.github_analyzer import GitHubAnalyzer


class AnalyzerAgent(BaseAgent):
    """AI-powered code analyzer for deployment planning"""
    
    def __init__(self, name: str, ai_client):
        super().__init__(name, ai_client)
        self.github_analyzer = GitHubAnalyzer()
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the codebase to understand its structure and requirements
        
        Returns:
            - languages: List of programming languages
            - frameworks: Detected frameworks
            - services: Identified services/components
            - dependencies: Key dependencies
            - entry_points: Main entry points
            - resource_hints: Initial resource requirements
        """
        request = context.get("request", {})
        source_type = request.get("source_type", "local")
        source_path = request.get("source_path", "")
        
        # Build analysis prompt
        system_prompt = """You are an expert DevOps engineer analyzing codebases for cloud deployment.

Analyze the provided codebase information and return a JSON object with:
{
  "languages": ["primary", "secondary"],
  "frameworks": ["framework1", "framework2"],
  "services": [
    {
      "name": "service_name",
      "type": "api|web|worker|database",
      "tech_stack": "framework/runtime",
      "entry_point": "main.py",
      "port": 8000
    }
  ],
  "dependencies": {
    "runtime": ["python3.11", "nodejs"],
    "databases": ["postgresql", "redis"],
    "external_services": ["s3", "sqs"]
  },
  "resource_hints": {
    "cpu_intensive": false,
    "memory_intensive": false,
    "io_intensive": false,
    "needs_gpu": false
  },
  "deployment_complexity": "simple|moderate|complex"
}

Be specific and accurate based on the code structure."""

        # Get code structure info
        code_info = self._get_code_structure(source_type, source_path)
        
        # Check if there was an error fetching the code
        if "error" in code_info and source_type == "github":
            # Don't call AI with empty data - return error immediately
            error_msg = code_info.get("message", code_info.get("error"))
            suggestions = code_info.get("suggestions", [])
            
            return {
                "analysis": {
                    "error": error_msg,
                    "source_type": source_type,
                    "source_path": source_path,
                    "suggestions": suggestions
                },
                "artifacts": [],
                "summary": f"❌ Failed to access repository: {error_msg}"
            }
        
        user_prompt = f"""Analyze this codebase for deployment:

Source Type: {source_type}
Source Path: {source_path}

Code Structure:
{json.dumps(code_info, indent=2)}

Provide comprehensive analysis for cloud deployment planning."""

        # Call AI for analysis
        try:
            response = await self._call_ai(system_prompt, user_prompt)
            analysis = self._extract_json(response)
            
            if not analysis:
                # Fallback to basic analysis
                analysis = self._basic_analysis(code_info)
            
            # Enhance with additional insights
            analysis["source_info"] = {
                "type": source_type,
                "path": source_path,
                "total_files": code_info.get("file_count", 0)
            }
            
            # Save artifact
            artifact_file = self._save_artifact(
                json.dumps(analysis, indent=2),
                "code_analysis.json",
                state
            )
            
            # Generate summary
            num_services = len(analysis.get("services", []))
            complexity = analysis.get("deployment_complexity", "unknown")
            primary_lang = analysis.get("languages", ["unknown"])[0]
            
            summary = f"Analyzed {primary_lang} project: {num_services} service(s), {complexity} complexity"
            
            return {
                "analysis": analysis,
                "artifacts": [artifact_file],
                "summary": summary
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            # Return basic fallback
            fallback = self._basic_analysis(code_info)
            return {
                "analysis": fallback,
                "artifacts": [],
                "summary": f"Basic analysis completed (AI unavailable: {str(e)})"
            }
    
    def _get_code_structure(self, source_type: str, source_path: str) -> Dict[str, Any]:
        """Extract code structure information"""
        
        if source_type == "github":
            # Analyze GitHub repository using API
            self.logger.info(f"Analyzing GitHub repository: {source_path}")
            
            # Extract branch if provided (format: url@branch or url)
            github_url = source_path
            branch = "main"
            
            if '@' in source_path:
                github_url, branch = source_path.split('@', 1)
            
            try:
                github_analysis = self.github_analyzer.analyze_repository(github_url, branch)
                
                if "error" in github_analysis:
                    error_msg = github_analysis["error"]
                    self.logger.error(f"GitHub analysis failed: {error_msg}")
                    
                    # Return clear error - don't proceed with fake data
                    return {
                        "source": "github",
                        "error": error_msg,
                        "url": github_url,
                        "branch": branch,
                        "message": f"Cannot access repository: {error_msg}. Repository may be private, not exist, or branch name is incorrect.",
                        "suggestions": [
                            "Check if repository URL is correct",
                            "Verify the repository is public",
                            "Try different branch name (main vs master)",
                            "If private, add GitHub token support (coming soon)"
                        ]
                    }
                
                # Tech stack is already included in github_analysis
                tech_stack = github_analysis.get("tech_stack", {})
                
                # Combine analysis with tech stack
                return {
                    "source": "github",
                    "url": github_url,
                    "branch": branch,
                    "structure": github_analysis.get("file_structure", {}),
                    "repo_info": github_analysis.get("repo_info", {}),
                    "tech_stack": tech_stack,
                    "dependencies": github_analysis.get("dependencies", {})
                }
            
            except Exception as e:
                self.logger.error(f"GitHub analysis exception: {e}")
                return {
                    "source": "github",
                    "error": str(e),
                    "url": github_url
                }
        
        elif source_type == "local" and os.path.exists(source_path):
            return self._analyze_local_path(source_path)
        
        elif source_type == "shipfast_job":
            return {
                "source": "shipfast_job",
                "job_id": source_path,
                "note": "Generated code from ShipFast workflow"
            }
        else:
            return {"source": source_type, "path": source_path}
    
    def _analyze_local_path(self, path: str) -> Dict[str, Any]:
        """Analyze local directory structure"""
        
        result = {
            "files": [],
            "directories": [],
            "file_count": 0,
            "extensions": {}
        }
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return result
            
            # Scan directory
            for item in path_obj.rglob("*"):
                # Skip hidden and common ignore patterns
                if any(part.startswith('.') for part in item.parts):
                    continue
                if any(part in ['node_modules', '__pycache__', 'venv', 'dist', 'build'] 
                       for part in item.parts):
                    continue
                
                if item.is_file():
                    result["file_count"] += 1
                    ext = item.suffix
                    result["extensions"][ext] = result["extensions"].get(ext, 0) + 1
                    
                    # Track important files
                    if item.name in ['package.json', 'requirements.txt', 'Dockerfile', 
                                    'docker-compose.yml', 'main.py', 'app.py', 'index.js']:
                        result["files"].append(str(item.relative_to(path_obj)))
                
                elif item.is_dir():
                    rel_path = str(item.relative_to(path_obj))
                    if rel_path and '/' not in rel_path:  # Top-level dirs only
                        result["directories"].append(rel_path)
            
            # Limit file list
            result["files"] = result["files"][:50]
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _basic_analysis(self, code_info: Dict[str, Any]) -> Dict[str, Any]:
        """Provide basic analysis when AI is unavailable"""
        
        source = code_info.get("source", "unknown")
        
        # Handle GitHub source
        if source == "github":
            return self._analyze_github_structure(code_info)
        
        # Handle local source
        extensions = code_info.get("extensions", {})
        
        # Detect languages
        languages = []
        if ".py" in extensions:
            languages.append("Python")
        if ".js" in extensions or ".ts" in extensions:
            languages.append("JavaScript")
        if ".go" in extensions:
            languages.append("Go")
        if ".java" in extensions:
            languages.append("Java")
        
        if not languages:
            languages = ["Unknown"]
        
        # Detect frameworks from files
        frameworks = []
        files = code_info.get("files", [])
        if any("requirements.txt" in f for f in files):
            frameworks.append("Python")
        if any("package.json" in f for f in files):
            frameworks.append("Node.js")
        
        return {
            "languages": languages,
            "frameworks": frameworks,
            "services": [
                {
                    "name": "main_service",
                    "type": "api",
                    "tech_stack": languages[0] if languages else "Unknown",
                    "entry_point": "main.py",
                    "port": 8000
                }
            ],
            "dependencies": {
                "runtime": [languages[0].lower() if languages else "unknown"],
                "databases": [],
                "external_services": []
            },
            "resource_hints": {
                "cpu_intensive": False,
                "memory_intensive": False,
                "io_intensive": False,
                "needs_gpu": False
            },
            "deployment_complexity": "simple",
            "source_info": code_info
        }
    
    def _analyze_github_structure(self, code_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze GitHub repository structure"""
        
        structure = code_info.get("structure", {})
        tech_stack = code_info.get("tech_stack", {})
        
        # Extract information
        folders = structure.get("folders", [])
        extensions = structure.get("extensions", {})
        important_files = structure.get("important_files", [])
        folder_structure = structure.get("folder_structure", {})
        deployment_hints = tech_stack.get("deployment_hints", {})
        
        # Detect languages
        languages = tech_stack.get("languages", [])
        if not languages:
            languages = ["Unknown"]
        
        # Detect frameworks
        frameworks = tech_stack.get("frameworks", [])
        
        # Identify services based on folder structure
        services = []
        
        # Check for app/ folder - important for Docker question
        has_app_folder = 'app' in folders or 'application' in folder_structure
        has_dockerfile = structure.get("has_dockerfile", False)
        has_docker_compose = structure.get("has_docker_compose", False)
        
        # Backend/API service
        if deployment_hints.get("has_backend") or deployment_hints.get("has_api"):
            services.append({
                "name": "backend_service",
                "type": "api",
                "tech_stack": languages[0] if languages else "Unknown",
                "entry_point": self._find_entry_point(structure.get("entry_points", []), "backend"),
                "port": 8000,
                "has_app_folder": has_app_folder
            })
        
        # Frontend service
        if deployment_hints.get("has_frontend"):
            services.append({
                "name": "frontend_service",
                "type": "web",
                "tech_stack": "React/Vue/Angular" if ".js" in extensions or ".ts" in extensions else "Unknown",
                "entry_point": "index.html",
                "port": 3000
            })
        
        # Worker service
        if 'workers' in folders or 'worker' in folders:
            services.append({
                "name": "worker_service",
                "type": "worker",
                "tech_stack": languages[0] if languages else "Unknown",
                "entry_point": "worker.py"
            })
        
        # Default service if none detected
        if not services:
            services.append({
                "name": "main_service",
                "type": "api",
                "tech_stack": languages[0] if languages else "Unknown",
                "entry_point": "main.py",
                "port": 8000,
                "has_app_folder": has_app_folder
            })
        
        # Detect databases
        databases = []
        if deployment_hints.get("has_database"):
            databases.append("postgresql")
        
        # Docker deployment questions
        docker_questions = []
        
        if has_app_folder and not has_dockerfile:
            docker_questions.append({
                "id": "docker_deployment",
                "question": "Your project has an 'app/' folder. Do you want to use Docker for deployment?",
                "type": "choice",
                "options": [
                    "Yes - Generate Dockerfile",
                    "Yes - Generate Docker Compose (multi-service)",
                    "No - Use direct deployment"
                ],
                "default": "Yes - Generate Dockerfile",
                "impact": "Docker provides consistent deployment environment and easier scaling"
            })
        
        if has_dockerfile and not has_docker_compose and len(services) > 1:
            docker_questions.append({
                "id": "docker_compose",
                "question": "You have multiple services. Want to orchestrate them with Docker Compose?",
                "type": "choice",
                "options": ["Yes", "No"],
                "default": "Yes",
                "impact": "Docker Compose simplifies multi-service deployment"
            })
        
        # Determine complexity
        complexity = "simple"
        if len(services) > 2 or deployment_hints.get("has_database"):
            complexity = "moderate"
        if len(services) > 3 and deployment_hints.get("has_database"):
            complexity = "complex"
        
        return {
            "languages": languages,
            "frameworks": frameworks,
            "services": services,
            "dependencies": {
                "runtime": [lang.lower() for lang in languages[:2]],
                "databases": databases,
                "external_services": []
            },
            "resource_hints": {
                "cpu_intensive": False,
                "memory_intensive": deployment_hints.get("has_database", False),
                "io_intensive": deployment_hints.get("has_database", False),
                "needs_gpu": False
            },
            "deployment_complexity": complexity,
            "docker_info": {
                "has_dockerfile": has_dockerfile,
                "has_docker_compose": has_docker_compose,
                "has_app_folder": has_app_folder,
                "questions": docker_questions
            },
            "folder_structure": {
                "folders": folders,
                "structure": folder_structure
            },
            "source_info": code_info
        }
    
    def _find_entry_point(self, entry_points: List[str], service_type: str) -> str:
        """Find appropriate entry point file"""
        
        if not entry_points:
            return "main.py"
        
        # Prefer service-specific entry points
        for ep in entry_points:
            if service_type in ep.lower():
                return ep
        
        # Return first entry point
        return entry_points[0]

