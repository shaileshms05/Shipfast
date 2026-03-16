import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/jobs');
      setJobs(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Feature Shipments</h1>
        <Link
          to="/ship"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Ship New Feature
        </Link>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-12 glass rounded-lg">
          <p className="text-gray-600 mb-4">No feature shipments yet</p>
          <Link to="/ship" className="text-blue-600 hover:underline">
            Ship your first feature →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}

function JobCard({ job }) {
  const statusColors = {
    queued: 'bg-gray-100 text-gray-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  };

  const statusIcons = {
    queued: <ClockIcon className="h-5 w-5" />,
    running: <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>,
    completed: <CheckCircleIcon className="h-5 w-5" />,
    failed: <XCircleIcon className="h-5 w-5" />
  };

  return (
    <Link to={`/job/${job.id}`} className="block">
      <div className="glass rounded-lg p-6 hover:shadow-xl transition-all">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-2">{job.featureRequest}</h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>{new Date(job.createdAt).toLocaleString()}</span>
              {job.progress > 0 && <span>{job.progress}% complete</span>}
            </div>
          </div>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${statusColors[job.status]}`}>
            {statusIcons[job.status]}
            <span className="font-medium capitalize">{job.status}</span>
          </div>
        </div>
        {job.stages.length > 0 && (
          <div className="mt-4 flex space-x-2">
            {['Requirements', 'Architecture', 'Code', 'Review', 'Integration', 'Deployment'].map((stage) => (
              <div
                key={stage}
                className={`h-2 flex-1 rounded-full ${
                  job.stages.find((s) => s.name === stage)
                    ? 'bg-green-500'
                    : 'bg-gray-200'
                }`}
              ></div>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}
