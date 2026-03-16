/**
 * ShipFast v3.0 - UI Server
 * 
 * Simple static file server for React app.
 * All API calls go directly to FastAPI backend on port 8000.
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Serve React build (check if build exists)
const buildPath = path.join(__dirname, 'client/build');
if (fs.existsSync(buildPath)) {
  console.log('✓ Serving React build from:', buildPath);
  app.use(express.static(buildPath));
} else {
  console.log('⚠️  React build not found. Run: cd client && npm run build');
  console.log('   Or run in dev mode: cd client && npm start');
}

// Health check (for UI server only)
app.get('/ui/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'ShipFast UI server running',
    backend: 'http://localhost:8000',
    note: 'All API calls go to FastAPI backend on port 8000'
  });
});

// Serve React app for any route (must be last)
app.get('*', (req, res) => {
  const indexPath = path.join(__dirname, 'client/build', 'index.html');
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.json({ 
      message: 'ShipFast UI Server',
      status: 'running',
      backend: 'http://localhost:8000',
      note: 'React build not found. Run: cd client && npm run build',
      hint: 'Or run React dev server: cd client && npm start'
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 ShipFast UI server running on port ${PORT}`);
  console.log(`   Frontend: http://localhost:${PORT}`);
  console.log(`   Backend API: http://localhost:8000`);
  console.log(`   API Docs: http://localhost:8000/docs`);
});
