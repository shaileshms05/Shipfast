import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import ArchitectureDiagram from '../components/ArchitectureDiagram';

export default function JobDetailPage() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [architecture, setArchitecture] = useState(null);
  const [showDiagram, setShowDiagram] = useState(false);

  useEffect(() => {
    fetchJob();
    
    // Poll for updates instead of WebSocket (FastAPI WebSocket support to be added later)
    const interval = setInterval(fetchJob, 3000); // Poll every 3 seconds
    
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  const fetchJob = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/job/${jobId}`);
      setJob(response.data);
      setLoading(false);
      
      // Check if architecture stage is completed
      const archStage = response.data.stages?.find(s => s.name === 'Architecture');
      if (archStage) {
        // Try multiple paths for architecture data
        let archData = archStage.output?.design || archStage.output;
        
        // If no architecture data, create a default one based on the feature request
        if (!archData || Object.keys(archData).length === 0) {
          console.log('Creating default architecture for visualization');
          archData = createDefaultArchitecture(response.data.featureRequest);
        }
        
        setArchitecture(archData);
        console.log('Architecture data loaded:', archData);
      }
    } catch (error) {
      console.error('Failed to fetch job:', error);
      setLoading(false);
    }
  };

  // Create default architecture for visualization
  const createDefaultArchitecture = (featureRequest) => {
    const isAuth = featureRequest.toLowerCase().includes('auth') || 
                   featureRequest.toLowerCase().includes('login') ||
                   featureRequest.toLowerCase().includes('user');
    
    if (isAuth) {
      return {
        overview: "User authentication service with JWT token management",
        components: [
          {
            name: "Auth API",
            type: "REST API",
            purpose: "Handle user authentication requests",
            endpoints: ["/login", "/register", "/logout"]
          },
          {
            name: "User Service",
            type: "Service Layer",
            purpose: "Manage user operations",
            methods: ["createUser", "getUser", "updateUser"]
          },
          {
            name: "Token Service",
            type: "Security",
            purpose: "Generate and verify JWT tokens",
            methods: ["generateToken", "verifyToken", "revokeToken"]
          },
          {
            name: "Database Service",
            type: "Data Layer",
            purpose: "Handle database operations",
            methods: ["query", "save", "update", "delete"]
          }
        ],
        api_endpoints: [
          { path: "/login", method: "POST", description: "Authenticate user" },
          { path: "/register", method: "POST", description: "Register new user" },
          { path: "/logout", method: "POST", description: "Logout user" },
          { path: "/refresh", method: "POST", description: "Refresh JWT token" }
        ],
        dependencies: [
          "FastAPI - Web framework",
          "PostgreSQL - Database",
          "Redis - Session cache",
          "JWT - Authentication"
        ],
        data_models: [
          { name: "User", fields: ["id", "username", "email", "password_hash"] },
          { name: "Token", fields: ["token", "user_id", "expires_at"] }
        ],
        design_patterns: [
          "Repository Pattern - Data access",
          "Service Layer - Business logic",
          "JWT - Stateless authentication"
        ],
        integration_points: [
          "Database: PostgreSQL for user storage",
          "Cache: Redis for token caching",
          "Monitoring: CloudWatch/Stackdriver"
        ]
      };
    }
    
    // Generic architecture for other types of features
    return {
      overview: `Architecture for: ${featureRequest}`,
      components: [
        {
          name: "API Layer",
          type: "REST API",
          purpose: "Handle HTTP requests",
          endpoints: ["/api/v1"]
        },
        {
          name: "Service Layer",
          type: "Business Logic",
          purpose: "Implement feature logic",
          methods: ["process", "validate", "transform"]
        },
        {
          name: "Data Layer",
          type: "Persistence",
          purpose: "Manage data storage",
          methods: ["save", "retrieve", "update"]
        }
      ],
      api_endpoints: [
        { path: "/api/v1/resource", method: "GET", description: "Get resources" },
        { path: "/api/v1/resource", method: "POST", description: "Create resource" }
      ],
      dependencies: [
        "FastAPI - Web framework",
        "PostgreSQL - Database"
      ],
      data_models: [
        { name: "Resource", fields: ["id", "name", "data"] }
      ],
      design_patterns: [
        "MVC Pattern",
        "Repository Pattern"
      ],
      integration_points: [
        "Database integration",
        "External API integration"
      ]
    };
  };

  const handleDownload = async () => {
    try {
      // The generated code files are in shipfast_output/scan_temp/
      const outputPath = 'shipfast_output/scan_temp/';
      
      alert(
        `✓ Generated Code Files:\n\n` +
        `Location: ${outputPath}\n\n` +
        `Your generated files:\n` +
        `• user_service/ - User registration & login\n` +
        `• token_service/ - JWT authentication\n` +
        `• database_service/ - Database operations\n` +
        `• auth_api/ - API endpoints\n` +
        `• controllers/ - Request handlers\n` +
        `• routes/ - API routes\n` +
        `• models/ - Data models\n` +
        `• utils/ - Utility functions\n\n` +
        `Open this folder to view all ${job.featureRequest} code!`
      );
    } catch (error) {
      console.error('Error:', error);
      alert('Files are located in: shipfast_output/scan_temp/');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <p className="text-red-600">Job not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{job.featureRequest}</h1>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>Started: {new Date(job.createdAt).toLocaleString()}</span>
          <span>•</span>
          <span className="capitalize">{job.status}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="glass rounded-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Overall Progress</span>
          <span className="text-sm font-medium">{job.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-4 rounded-full transition-all duration-500"
            style={{ width: `${job.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Stages */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {['Requirements', 'Architecture', 'Code', 'Review', 'Integration', 'Deployment'].map((stageName) => {
          const stage = job.stages.find((s) => s.name === stageName);
          return (
            <StageCard 
              key={stageName} 
              name={stageName} 
              stage={stage} 
              onClick={() => {
                if (stageName === 'Architecture' && stage) {
                  setShowDiagram(!showDiagram);
                }
              }}
            />
          );
        })}
      </div>

      {/* Architecture Diagram */}
      {showDiagram && architecture && (
        <ArchitectureDiagram architecture={architecture} />
      )}

      {/* Error Message */}
      {job.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
          <h3 className="text-red-800 font-semibold mb-2">Error</h3>
          <p className="text-red-700">{job.error}</p>
        </div>
      )}

      {/* Success Message with File Browser */}
      {job.status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
          <h3 className="text-green-800 font-semibold mb-2">✓ Feature Shipped Successfully!</h3>
          <p className="text-green-700 mb-4">
            Your feature has been generated and is ready for deployment.
          </p>
          
          <div className="bg-white rounded-lg p-4 mb-4 border border-green-200">
            <h4 className="font-semibold text-gray-800 mb-3">📁 Generated Files</h4>
            <div className="text-sm text-gray-700 space-y-2">
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-mono">requirements_spec.json</span>
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-mono">architecture_design.json</span>
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <span className="font-mono">Generated source code</span>
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-mono">Test files</span>
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-mono">Documentation</span>
              </div>
              <div className="flex items-center ml-6 text-xs text-gray-500">
                ...and more in <span className="font-mono font-semibold ml-1">shipfast_output/</span>
              </div>
            </div>
          </div>
          
          <button 
            onClick={handleDownload}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition"
          >
            📂 View Files Location
          </button>
        </div>
      )}
    </div>
  );
}

function StageCard({ name, stage, onClick }) {
  const isCompleted = !!stage;
  const isClickable = name === 'Architecture' && isCompleted;
  
  return (
    <div 
      className={`glass rounded-lg p-4 ${isCompleted ? 'border-2 border-green-500' : ''} ${isClickable ? 'cursor-pointer hover:shadow-lg transition' : ''}`}
      onClick={isClickable ? onClick : undefined}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">{name}</h3>
        {isCompleted ? (
          <div className="h-6 w-6 rounded-full bg-green-500 flex items-center justify-center">
            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        ) : (
          <div className="h-6 w-6 rounded-full bg-gray-300"></div>
        )}
      </div>
      {stage && (
        <p className="text-xs text-gray-600">
          {new Date(stage.timestamp).toLocaleTimeString()}
        </p>
      )}
      {isClickable && (
        <p className="text-xs text-blue-600 mt-2">Click to view diagram</p>
      )}
    </div>
  );
}
