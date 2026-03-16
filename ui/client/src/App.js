import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ShipPage from './pages/ShipPage';
import JobsPage from './pages/JobsPage';
import JobDetailPage from './pages/JobDetailPage';
import DocsPage from './pages/DocsPage';
import DeployPage from './pages/DeployPage';

function App() {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Check server connection
    fetch('http://localhost:8000/health')
      .then(() => setConnected(true))
      .catch(() => setConnected(false));
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="glass shadow-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link to="/" className="flex-shrink-0 flex items-center">
                  <span className="text-2xl font-bold gradient-text">⚡ ShipFast</span>
                </Link>
                <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                  <Link
                    to="/"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-blue-600"
                  >
                    Home
                  </Link>
                  <Link
                    to="/ship"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    Ship Feature
                  </Link>
                  <Link
                    to="/deploy"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    🚀 Deploy
                  </Link>
                  <Link
                    to="/jobs"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    Jobs
                  </Link>
                  <Link
                    to="/docs"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    Docs
                  </Link>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex items-center space-x-2">
                  <div className={`h-2 w-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-600">
                    {connected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/ship" element={<ShipPage />} />
            <Route path="/deploy" element={<DeployPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/job/:jobId" element={<JobDetailPage />} />
            <Route path="/docs" element={<DocsPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="text-center text-sm text-gray-500">
              <p>Built with ❤️ by ShipFast</p>
              <p className="mt-2">Powered by Cerebras (Llama 3.3 70B) • FREE & Fast</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
