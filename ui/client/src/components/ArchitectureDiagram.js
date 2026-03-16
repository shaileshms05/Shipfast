import React from 'react';

export default function ArchitectureDiagram({ architecture }) {
  if (!architecture || !architecture.components) {
    return null;
  }

  const components = architecture.components || [];
  const apiEndpoints = architecture.api_endpoints || [];
  const dependencies = architecture.dependencies || [];

  return (
    <div className="glass rounded-lg p-6 mb-8">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        <svg className="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        Architecture Flow Diagram
      </h2>

      {/* Overview */}
      <div className="mb-8 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Overview</h3>
        <p className="text-blue-800 text-sm">{architecture.overview}</p>
      </div>

      {/* Flow Diagram */}
      <div className="relative">
        {/* Client/User */}
        <div className="flex justify-center mb-8">
          <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-lg shadow-lg font-semibold">
            👤 Client / User
          </div>
        </div>

        {/* Arrow Down */}
        <div className="flex justify-center mb-4">
          <svg className="w-6 h-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 4v16m0 0l-4-4m4 4l4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          </svg>
        </div>

        {/* API Endpoints */}
        {apiEndpoints.length > 0 && (
          <>
            <div className="flex justify-center mb-4">
              <div className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg max-w-md text-center">
                <div className="font-semibold mb-2">🌐 API Endpoints</div>
                {apiEndpoints.map((endpoint, idx) => (
                  <div key={idx} className="text-xs mt-1 bg-green-600 rounded px-2 py-1">
                    {endpoint.method || 'GET'} {endpoint.path}
                  </div>
                ))}
              </div>
            </div>

            {/* Arrow Down */}
            <div className="flex justify-center mb-4">
              <svg className="w-6 h-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m0 0l-4-4m4 4l4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              </svg>
            </div>
          </>
        )}

        {/* Components */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {components.map((component, idx) => (
            <ComponentBox key={idx} component={component} />
          ))}
        </div>

        {/* Dependencies Section */}
        {dependencies.length > 0 && (
          <>
            {/* Arrow Down */}
            <div className="flex justify-center mb-4">
              <svg className="w-6 h-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m0 0l-4-4m4 4l4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              </svg>
            </div>

            <div className="bg-yellow-50 rounded-lg border-2 border-yellow-200 p-4 mb-4">
              <h3 className="font-semibold text-yellow-900 mb-3 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                External Dependencies
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {dependencies.map((dep, idx) => (
                  <div key={idx} className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded text-sm">
                    📦 {dep}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Database/Storage (if mentioned) */}
        {architecture.data_models && architecture.data_models.length > 0 && (
          <>
            {/* Arrow Down */}
            <div className="flex justify-center mb-4">
              <svg className="w-6 h-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m0 0l-4-4m4 4l4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              </svg>
            </div>

            <div className="flex justify-center">
              <div className="bg-gradient-to-r from-indigo-500 to-blue-500 text-white px-6 py-3 rounded-lg shadow-lg max-w-md">
                <div className="font-semibold mb-2 flex items-center justify-center">
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                  Database / Storage
                </div>
                {architecture.data_models.map((model, idx) => (
                  <div key={idx} className="text-xs mt-1 bg-indigo-600 rounded px-2 py-1">
                    {model.name}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Design Patterns */}
      {architecture.design_patterns && architecture.design_patterns.length > 0 && (
        <div className="mt-8 p-4 bg-purple-50 rounded-lg border-2 border-purple-200">
          <h3 className="font-semibold text-purple-900 mb-3">🎨 Design Patterns</h3>
          <div className="flex flex-wrap gap-2">
            {architecture.design_patterns.map((pattern, idx) => (
              <span key={idx} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                {pattern}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Integration Points */}
      {architecture.integration_points && architecture.integration_points.length > 0 && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-3">🔗 Integration Points</h3>
          <ul className="space-y-2">
            {architecture.integration_points.map((point, idx) => (
              <li key={idx} className="text-sm text-gray-700 flex items-start">
                <svg className="w-4 h-4 mr-2 mt-0.5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ComponentBox({ component }) {
  const getComponentIcon = (type) => {
    const lowerType = (type || component.type || '').toLowerCase();
    if (lowerType.includes('api') || lowerType.includes('endpoint')) return '🌐';
    if (lowerType.includes('service')) return '⚙️';
    if (lowerType.includes('controller')) return '🎮';
    if (lowerType.includes('model') || lowerType.includes('data')) return '📊';
    if (lowerType.includes('middleware') || lowerType.includes('auth')) return '🔐';
    if (lowerType.includes('util') || lowerType.includes('helper')) return '🛠️';
    if (lowerType.includes('database') || lowerType.includes('storage')) return '💾';
    return '📦';
  };

  const getComponentColor = (idx) => {
    const colors = [
      'from-blue-400 to-blue-600',
      'from-green-400 to-green-600',
      'from-orange-400 to-orange-600',
      'from-pink-400 to-pink-600',
      'from-teal-400 to-teal-600',
      'from-indigo-400 to-indigo-600',
    ];
    return colors[idx % colors.length];
  };

  return (
    <div className={`bg-gradient-to-br ${getComponentColor(0)} text-white rounded-lg shadow-lg p-4 transform transition hover:scale-105`}>
      <div className="flex items-start justify-between mb-2">
        <div className="text-2xl">{getComponentIcon(component.type)}</div>
        {component.type && (
          <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">
            {component.type}
          </span>
        )}
      </div>
      <h4 className="font-bold mb-2 text-sm">{component.name}</h4>
      <p className="text-xs opacity-90 mb-3">{component.description}</p>
      
      {component.dependencies && component.dependencies.length > 0 && (
        <div className="text-xs">
          <div className="font-semibold mb-1">Dependencies:</div>
          <div className="space-y-1">
            {component.dependencies.slice(0, 2).map((dep, idx) => (
              <div key={idx} className="bg-white bg-opacity-20 rounded px-2 py-0.5 truncate">
                {dep}
              </div>
            ))}
            {component.dependencies.length > 2 && (
              <div className="text-xs opacity-75">+{component.dependencies.length - 2} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
