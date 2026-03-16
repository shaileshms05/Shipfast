"""
ShipFast v3.0 - FastAPI Server
Main API server with unified orchestration for ShipFast and Deploy workflows
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import UnifiedOrchestrator
from core.state import WorkflowType, create_shipfast_workflow, create_deploy_workflow
from services.ai.cerebras import CerebrasClient

# Initialize logger
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="ShipFast v3.0 API",
    description="AI-Powered Development Automation Platform",
    version="3.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
workflows: Dict[str, Any] = {}
orchestrator: Optional[UnifiedOrchestrator] = None

# Pydantic models for request/response
class ShipFastRequest(BaseModel):
    feature_description: str
    use_langgraph: Optional[bool] = False

class DeployAnalyzeRequest(BaseModel):
    source_type: str  # "github", "local", "shipfast"
    source_path: Optional[str] = None
    github_url: Optional[str] = None
    github_branch: Optional[str] = "main"
    local_path: Optional[str] = None
    job_id: Optional[str] = None
    use_langgraph: Optional[bool] = False
    
    def __init__(self, **data):
        super().__init__(**data)
        # Support both source_path and github_url
        if self.source_path and not self.github_url and self.source_type == "github":
            self.github_url = self.source_path


# Background task to execute workflow
async def execute_workflow_task(workflow_id: str, use_langgraph: bool = False):
    """Background task to execute workflow"""
    try:
        state = workflows.get(workflow_id)
        if not state:
            logger.error("Workflow not found", workflow_id=workflow_id)
            return
        
        # Execute workflow using orchestrator
        if orchestrator:
            await orchestrator.execute(state)
        else:
            logger.error("Orchestrator not initialized")
            
    except Exception as e:
        logger.error("Workflow execution failed", error=str(e), workflow_id=workflow_id)


# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "3.0.0"}


# ShipFast Core endpoints
@app.post("/api/ship")
async def ship_feature(
    request: ShipFastRequest,
    background_tasks: BackgroundTasks,
):
    """Ship a new feature using ShipFast agents"""
    try:
        # Create ShipFast workflow
        state = create_shipfast_workflow(request.feature_description)
        
        # Store workflow
        workflows[state.id] = state
        
        # Start background execution
        background_tasks.add_task(
            execute_workflow_task,
            state.id,
            request.use_langgraph
        )
        
        logger.info(
            "ShipFast workflow created",
            workflow_id=state.id,
            feature=request.feature_description[:50]
        )
        
        return {
            "job_id": state.id,
            "status": "queued",
            "message": "Feature development workflow started",
            "orchestrator": "basic",
        }
        
    except Exception as e:
        logger.error("Failed to create ShipFast workflow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    """Get job status and results"""
    if job_id not in workflows:
        raise HTTPException(status_code=404, detail="Job not found")
    
    state = workflows[job_id]
    return state.to_dict()


@app.get("/api/jobs")
def get_all_jobs():
    """Get all jobs"""
    jobs = [state.to_dict() for state in workflows.values()]
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    return jobs


# ShipFast Deploy endpoints
@app.post("/api/deploy/analyze")
async def deploy_analyze(
    request: DeployAnalyzeRequest,
    background_tasks: BackgroundTasks,
):
    """Analyze code for deployment"""
    try:
        # Create deploy workflow
        source = {
            "source_type": request.source_type,
            "source_path": request.source_path or request.github_url,
            "github_url": request.github_url or request.source_path,
            "github_branch": request.github_branch,
            "local_path": request.local_path or "test_deploy",
            "job_id": request.job_id,
        }
        
        state = create_deploy_workflow(source)
        
        # Store workflow
        workflows[state.id] = state
        
        # Start background execution
        background_tasks.add_task(
            execute_workflow_task,
            state.id,
            request.use_langgraph
        )
        
        logger.info(
            "Deploy analysis requested",
            workflow_id=state.id,
            source_type=request.source_type,
            use_langgraph=request.use_langgraph,
        )
        
        return {
            "analysis_id": state.id,
            "status": "queued",
            "message": "Deployment analysis queued",
            "orchestrator": "basic",
        }
        
    except Exception as e:
        logger.error("Failed to create deploy analysis", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deploy/{deploy_id}")
def get_deploy(deploy_id: str):
    """Get deployment status"""
    if deploy_id not in workflows:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    state = workflows[deploy_id]
    return state.to_dict()


# Statistics endpoint
@app.get("/api/stats")
def get_stats():
    """Get system statistics"""
    return {
        "total_workflows": len(workflows),
        "shipfast_workflows": len([w for w in workflows.values() if w.workflow_type == WorkflowType.SHIPFAST]),
        "deploy_workflows": len([w for w in workflows.values() if w.workflow_type == WorkflowType.DEPLOY]),
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global orchestrator
    
    try:
        # Initialize AI client
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            logger.error("CEREBRAS_API_KEY not found in environment")
            raise ValueError("CEREBRAS_API_KEY is required")
        
        ai_client = CerebrasClient(api_key=api_key)
        
        # Initialize orchestrator
        orchestrator = UnifiedOrchestrator(ai_client)
        
        logger.info("ShipFast v3.0 starting", port=8000)
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise


# Run server
if __name__ == "__main__":
    import uvicorn
    
    # Print startup banner
    print("\n" + "=" * 70)
    print("🚀 ShipFast v3.0 - AI-Powered Development Automation")
    print("=" * 70)
    print("\nFeatures:")
    print("  • ShipFast Core - 6-agent feature development")
    print("  • ShipFast Deploy - Intelligent deployment automation")
    print(f"\nServer: http://0.0.0.0:8000")
    print(f"API Docs: http://0.0.0.0:8000/docs")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
