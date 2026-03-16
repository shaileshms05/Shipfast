"""
ShipFast Deploy - Provisioner Agent
Generates Infrastructure as Code and deployment artifacts
"""

from typing import Dict, Any
from agents.base import BaseAgent
from core.state import WorkflowState, Stage
import structlog


class ProvisionerAgent(BaseAgent):
    """Infrastructure provisioning and IaC generation agent"""
    
    def __init__(self, name: str, ai_client):
        super().__init__(name, ai_client)
        self.logger = structlog.get_logger(name)
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate IaC and deployment artifacts"""
        result = {
            "artifacts": [],
            "deployment_steps": [],
        }
        
        try:
            # Get data from previous stages
            analysis = context.get("analysis", {})
            architecture = context.get("architecture", {})
            
            if not architecture:
                result["error"] = "No architecture data available"
                return result
            
            # Generate Terraform IaC
            terraform = self._generate_terraform(architecture)
            result["artifacts"].append({
                "type": "terraform",
                "filename": "main.tf",
                "content": terraform,
            })
            
            # Generate Dockerfile
            dockerfile = self._generate_dockerfile(analysis)
            result["artifacts"].append({
                "type": "docker",
                "filename": "Dockerfile",
                "content": dockerfile,
            })
            
            # Generate docker-compose
            docker_compose = self._generate_docker_compose(analysis)
            result["artifacts"].append({
                "type": "docker-compose",
                "filename": "docker-compose.yml",
                "content": docker_compose,
            })
            
            # Generate deployment steps
            result["deployment_steps"] = self._generate_deployment_steps(architecture)
            
            self.logger.info(
                "Provisioning artifacts generated",
                artifacts=len(result["artifacts"]),
                steps=len(result["deployment_steps"]),
            )
            
        except Exception as e:
            self.logger.error("Provisioning failed", error=str(e))
            result["error"] = str(e)
        
        return result
    
    def _generate_terraform(self, architecture: Dict[str, Any]) -> str:
        """Generate Terraform configuration"""
        
        terraform = """# Terraform Configuration for ShipFast Deploy
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "app_name" {
  default = "shipfast-app"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  
  enable_deletion_protection = false
}

# S3 Bucket for static assets
resource "aws_s3_bucket" "assets" {
  bucket = "${var.app_name}-assets"
}

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "load_balancer_dns" {
  value = aws_lb.main.dns_name
}
"""
        return terraform
    
    def _generate_dockerfile(self, analysis: Dict[str, Any]) -> str:
        """Generate Dockerfile"""
        
        tech_stack = analysis.get("tech_stack", {})
        languages = tech_stack.get("languages", [])
        
        if "Python" in languages:
            dockerfile = """# Dockerfile for Python Application
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        elif "JavaScript" in languages or "TypeScript" in languages:
            dockerfile = """# Dockerfile for Node.js Application
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --production

# Copy application
COPY . .

# Build if needed
RUN npm run build || true

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
"""
        else:
            dockerfile = """# Generic Dockerfile
FROM ubuntu:22.04

WORKDIR /app

# Copy application
COPY . .

# Expose port
EXPOSE 8000

CMD ["./start.sh"]
"""
        
        return dockerfile
    
    def _generate_docker_compose(self, analysis: Dict[str, Any]) -> str:
        """Generate docker-compose.yml"""
        
        compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
  
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
        return compose
    
    def _generate_deployment_steps(self, architecture: Dict[str, Any]) -> list:
        """Generate step-by-step deployment guide"""
        
        steps = [
            {
                "step": 1,
                "title": "Prerequisites",
                "commands": [
                    "Install AWS CLI: https://aws.amazon.com/cli/",
                    "Install Terraform: https://www.terraform.io/downloads",
                    "Install Docker: https://www.docker.com/get-started",
                ],
            },
            {
                "step": 2,
                "title": "Configure AWS Credentials",
                "commands": [
                    "aws configure",
                ],
            },
            {
                "step": 3,
                "title": "Initialize Terraform",
                "commands": [
                    "terraform init",
                    "terraform plan",
                ],
            },
            {
                "step": 4,
                "title": "Deploy Infrastructure",
                "commands": [
                    "terraform apply -auto-approve",
                ],
            },
            {
                "step": 5,
                "title": "Build and Push Docker Image",
                "commands": [
                    "docker build -t shipfast-app .",
                    "docker tag shipfast-app:latest <ECR_URL>/shipfast-app:latest",
                    "docker push <ECR_URL>/shipfast-app:latest",
                ],
            },
            {
                "step": 6,
                "title": "Deploy to ECS",
                "commands": [
                    "aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment",
                ],
            },
        ]
        
        return steps
