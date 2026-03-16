import React from 'react';

export default function DocsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold mb-8">Documentation</h1>
      
      <div className="space-y-8">
        <Section title="Getting Started">
          <p className="mb-4">
            ShipFast is an AI-powered development team that takes you from feature request
            to production deployment in minutes.
          </p>
          <h3 className="font-semibold mb-2">Quick Start:</h3>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Enter your feature request in the Ship page</li>
            <li>Watch as 6 AI agents work together to build it</li>
            <li>Download the generated code, tests, docs, and deployment configs</li>
            <li>Deploy to AWS, GCP, Azure, or DigitalOcean</li>
          </ol>
        </Section>

        <Section title="The 6 AI Agents">
          <div className="space-y-4">
            <AgentDoc
              name="Requirements Agent"
              emoji="📋"
              description="Analyzes your feature request, asks clarifying questions, and generates a detailed specification with acceptance criteria."
            />
            <AgentDoc
              name="Architect Agent"
              emoji="🏗️"
              description="Reviews your existing codebase, detects patterns, and proposes an architecture that fits naturally."
            />
            <AgentDoc
              name="Code Agent"
              emoji="💻"
              description="Implements the feature with best practices, proper error handling, type hints, and documentation."
            />
            <AgentDoc
              name="Review Agent"
              emoji="🔍"
              description="Checks for security vulnerabilities, performance issues, and code quality. Runs SonarQube, Checkov, and Trivy scans."
            />
            <AgentDoc
              name="Integration Agent"
              emoji="🔧"
              description="Generates comprehensive tests, API documentation, and updates deployment configurations."
            />
            <AgentDoc
              name="Deployment Agent"
              emoji="🚀"
              description="Creates Terraform configurations for AWS, GCP, Azure, or DigitalOcean with one-command deployment."
            />
          </div>
        </Section>

        <Section title="Features">
          <ul className="space-y-2 text-gray-700">
            <li>✅ <strong>Multi-agent collaboration</strong> - Agents work together seamlessly</li>
            <li>✅ <strong>Context-aware</strong> - Analyzes your existing codebase</li>
            <li>✅ <strong>Security scanning</strong> - SonarQube, Checkov, Trivy integration</li>
            <li>✅ <strong>Terraform deployment</strong> - Auto-generate IaC for any cloud</li>
            <li>✅ <strong>Free & Fast</strong> - Powered by Cerebras (Llama 3.3 70B)</li>
          </ul>
        </Section>

        <Section title="Example Requests">
          <div className="space-y-2">
            <ExampleRequest>Add user authentication with OAuth2 and JWT tokens</ExampleRequest>
            <ExampleRequest>Add REST API for managing todo items with CRUD operations</ExampleRequest>
            <ExampleRequest>Add payment processing with Stripe integration</ExampleRequest>
            <ExampleRequest>Add Redis caching layer for database queries</ExampleRequest>
            <ExampleRequest>Add admin dashboard with user management</ExampleRequest>
          </div>
        </Section>

        <Section title="Cloud Deployment">
          <p className="mb-4">
            ShipFast automatically generates Terraform configurations for your chosen cloud provider:
          </p>
          <div className="grid grid-cols-2 gap-4">
            <CloudProvider name="AWS" cost="~$25-35/month" />
            <CloudProvider name="GCP" cost="~$15-25/month" />
            <CloudProvider name="Azure" cost="~$20-30/month" />
            <CloudProvider name="DigitalOcean" cost="~$12-24/month" />
          </div>
        </Section>

        <Section title="Support">
          <p className="text-gray-700">
            For more information, see the complete documentation in the GitHub repository.
          </p>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="glass rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      {children}
    </div>
  );
}

function AgentDoc({ name, emoji, description }) {
  return (
    <div className="border-l-4 border-blue-500 pl-4 py-2">
      <h4 className="font-semibold text-lg mb-1">
        {emoji} {name}
      </h4>
      <p className="text-gray-700">{description}</p>
    </div>
  );
}

function ExampleRequest({ children }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700">
      "{children}"
    </div>
  );
}

function CloudProvider({ name, cost }) {
  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h4 className="font-semibold mb-1">{name}</h4>
      <p className="text-sm text-gray-600">{cost}</p>
    </div>
  );
}
