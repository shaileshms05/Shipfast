import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { SparklesIcon, RocketLaunchIcon } from '@heroicons/react/24/outline';

export default function ShipPage() {
  const navigate = useNavigate();
  const [featureRequest, setFeatureRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const examples = [
    'Add user authentication with OAuth2 and JWT tokens',
    'Add REST API for managing todo items with CRUD operations',
    'Add payment processing with Stripe integration',
    'Add email notification system with templates',
    'Add admin dashboard with user management',
    'Add Redis caching layer for database queries'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!featureRequest.trim()) {
      setError('Please enter a feature request');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/api/ship', {
        feature_request: featureRequest.trim()
      });

      // Redirect to job detail page
      navigate(`/job/${response.data.jobId}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit feature request. Make sure the backend server is running on port 8000.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-4">
          <RocketLaunchIcon className="h-16 w-16 text-blue-600" />
        </div>
        <h1 className="text-4xl font-bold gradient-text mb-4">
          Ship a New Feature
        </h1>
        <p className="text-xl text-gray-600">
          Describe what you want to build, and our AI agents will handle the rest
        </p>
      </div>

      {/* Feature Request Form */}
      <div className="glass rounded-2xl p-8 mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label htmlFor="feature" className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to build?
            </label>
            <textarea
              id="feature"
              rows="6"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-lg"
              placeholder="Example: Add user authentication with OAuth2 and JWT tokens"
              value={featureRequest}
              onChange={(e) => setFeatureRequest(e.target.value)}
              disabled={loading}
            />
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !featureRequest.trim()}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-lg font-semibold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                <span>Shipping...</span>
              </>
            ) : (
              <>
                <SparklesIcon className="h-6 w-6" />
                <span>Ship Feature</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Examples */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <SparklesIcon className="h-6 w-6 text-yellow-500 mr-2" />
          Example Feature Requests
        </h2>
        <div className="space-y-3">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => setFeatureRequest(example)}
              className="w-full text-left glass rounded-lg p-4 hover:shadow-lg transition-all hover:scale-[1.02]"
              disabled={loading}
            >
              <p className="text-gray-700">{example}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
        <ul className="space-y-2 text-blue-800">
          <li>• Requirements Agent analyzes your request</li>
          <li>• Architect Agent designs the architecture</li>
          <li>• Code Agent implements the feature</li>
          <li>• Review Agent checks for security & quality</li>
          <li>• Integration Agent creates tests & docs</li>
          <li>• Deployment Agent prepares deployment configs</li>
        </ul>
        <p className="mt-4 text-blue-900">
          ⏱️ <strong>Typical time:</strong> 3-5 minutes
        </p>
      </div>
    </div>
  );
}
