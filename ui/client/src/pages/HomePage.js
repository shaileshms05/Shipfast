import React from 'react';
import { Link } from 'react-router-dom';
import { RocketLaunchIcon, BoltIcon, ShieldCheckIcon, CloudIcon } from '@heroicons/react/24/outline';

export default function HomePage() {
  return (
    <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 min-h-screen">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-6xl font-bold gradient-text mb-6">
            Ship Features at Lightning Speed
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            From feature request to production in minutes. AI agents handle requirements,
            architecture, code, review, testing, and deployment automatically.
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              to="/ship"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              Ship Your First Feature →
            </Link>
            <Link
              to="/docs"
              className="bg-white text-gray-700 px-8 py-4 rounded-lg font-semibold text-lg hover:shadow-xl transition-all border border-gray-200"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={<RocketLaunchIcon className="h-8 w-8 text-blue-600" />}
            title="6 AI Agents"
            description="Requirements, Architecture, Code, Review, Integration, and Deployment agents working together"
          />
          <FeatureCard
            icon={<BoltIcon className="h-8 w-8 text-yellow-600" />}
            title="Ultra Fast"
            description="Powered by Cerebras Llama 3.3 70B - 20x faster than GPT-4"
          />
          <FeatureCard
            icon={<ShieldCheckIcon className="h-8 w-8 text-green-600" />}
            title="Security Built-In"
            description="SonarQube, Checkov, and Trivy scanning automatically"
          />
          <FeatureCard
            icon={<CloudIcon className="h-8 w-8 text-purple-600" />}
            title="Deploy Anywhere"
            description="Auto-generate Terraform for AWS, GCP, Azure, or DigitalOcean"
          />
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-center mb-12">How It Works</h2>
        <div className="space-y-8">
          <Step
            number="1"
            title="Enter Feature Request"
            description='Simply describe what you want: "Add user authentication with OAuth2"'
            color="blue"
          />
          <Step
            number="2"
            title="AI Agents Work"
            description="6 specialized agents analyze, design, implement, review, test, and prepare deployment"
            color="purple"
          />
          <Step
            number="3"
            title="Review & Deploy"
            description="Get production-ready code, tests, docs, and deployment configs in minutes"
            color="green"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="glass rounded-2xl p-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <Stat value="3-5 min" label="Average Time" />
            <Stat value="$0" label="Cost (Free Cerebras)" />
            <Stat value="10-100x" label="Faster Than Manual" />
            <Stat value="4" label="Cloud Providers" />
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-4xl font-bold mb-6">Ready to Ship?</h2>
        <p className="text-xl text-gray-600 mb-8">
          Start building features 10x faster today
        </p>
        <Link
          to="/ship"
          className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-12 py-4 rounded-lg font-semibold text-lg hover:shadow-2xl transition-all transform hover:scale-105"
        >
          Get Started Free →
        </Link>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="glass rounded-xl p-6 hover:shadow-xl transition-all">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

function Step({ number, title, description, color }) {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    green: 'from-green-500 to-green-600'
  };

  return (
    <div className="flex items-start space-x-6">
      <div className={`flex-shrink-0 w-16 h-16 rounded-full bg-gradient-to-br ${colors[color]} flex items-center justify-center text-white text-2xl font-bold shadow-lg`}>
        {number}
      </div>
      <div className="flex-1">
        <h3 className="text-2xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 text-lg">{description}</p>
      </div>
    </div>
  );
}

function Stat({ value, label }) {
  return (
    <div>
      <div className="text-4xl font-bold gradient-text mb-2">{value}</div>
      <div className="text-gray-600">{label}</div>
    </div>
  );
}
