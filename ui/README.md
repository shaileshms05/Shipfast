# ShipFast Web UI

Beautiful, modern web interface for ShipFast - your AI development team.

## Features

- 🎨 **Modern UI** - Beautiful, responsive design with Tailwind CSS
- ⚡ **Real-time Updates** - WebSocket connection for live progress
- 📊 **Job Dashboard** - View all feature shipments and their status
- 🔍 **Detailed Progress** - See each agent working in real-time
- 💾 **File Downloads** - Download generated code, tests, docs, and configs
- 📱 **Mobile Responsive** - Works perfectly on all devices

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.11+ (for ShipFast backend)
- ShipFast already set up (see main README)

### Installation

```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm run install-all

# This installs:
# - Backend dependencies (Express, WebSocket)
# - Frontend dependencies (React, Tailwind CSS)
```

### Running the UI

#### Development Mode

```bash
# Start both frontend and backend
npm run dev

# This runs:
# - Backend server on http://localhost:5000
# - React app on http://localhost:3000
```

#### Production Mode

```bash
# Build React app
cd client && npm run build

# Start production server
npm start

# Access at http://localhost:5000
```

## Architecture

```
ui/
├── server.js              # Express backend + WebSocket
├── package.json           # Backend dependencies
│
└── client/
    ├── src/
    │   ├── App.js         # Main React component
    │   ├── index.js       # React entry point
    │   ├── index.css      # Global styles (Tailwind)
    │   └── pages/
    │       ├── HomePage.js          # Landing page
    │       ├── ShipPage.js          # Submit feature request
    │       ├── JobsPage.js          # View all jobs
    │       ├── JobDetailPage.js     # Real-time job progress
    │       └── DocsPage.js          # Documentation
    │
    ├── public/
    │   └── index.html     # HTML template
    │
    └── package.json       # Frontend dependencies
```

## Pages

### 1. Home Page (`/`)

**Features:**
- Hero section with gradient background
- Feature cards showcasing capabilities
- How it works section
- Stats and CTA

**Components:**
- FeatureCard - Highlights key features
- Step - Visual workflow steps
- Stat - Statistics display

### 2. Ship Page (`/ship`)

**Features:**
- Large textarea for feature requests
- Example requests (one-click)
- Submit to start shipping
- Real-time feedback

**Flow:**
1. User enters feature request
2. Click "Ship Feature"
3. Redirects to job detail page
4. Watch agents work in real-time

### 3. Jobs Page (`/jobs`)

**Features:**
- List of all feature shipments
- Status badges (queued, running, completed, failed)
- Progress bars for running jobs
- Click to view details

**Auto-refresh:** Every 5 seconds

### 4. Job Detail Page (`/job/:jobId`)

**Features:**
- Real-time progress updates (WebSocket)
- 6 agent stages with completion status
- Overall progress bar
- Error messages
- Download generated files

**WebSocket Events:**
- `subscribe` - Subscribe to job updates
- `job_update` - Receive progress updates

### 5. Docs Page (`/docs`)

**Features:**
- Getting started guide
- Agent descriptions
- Example requests
- Cloud deployment info

## Backend API

### REST Endpoints

**Health Check**
```
GET /api/health
Response: { status: 'ok', message: 'ShipFast server running' }
```

**Submit Feature Request**
```
POST /api/ship
Body: { featureRequest: string, config?: object }
Response: { jobId: string, status: 'queued' }
```

**Get Job Status**
```
GET /api/job/:jobId
Response: { 
  id, featureRequest, status, progress, 
  stages: [], createdAt, error? 
}
```

**List All Jobs**
```
GET /api/jobs
Response: [{ job1 }, { job2 }, ...]
```

**Get Generated Files**
```
GET /api/files/:jobId
Response: { files: [{ name, path, size, modified }] }
```

**Download File**
```
GET /api/download/:jobId/:filename
Response: File download
```

### WebSocket Protocol

**Connect**
```javascript
const ws = new WebSocket('ws://localhost:5000');
```

**Subscribe to Job**
```javascript
ws.send(JSON.stringify({ 
  type: 'subscribe', 
  jobId: 'job_123' 
}));
```

**Receive Updates**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type === 'job_update'
  // data.job = { ...job details }
};
```

## Styling

### Tailwind CSS

Custom classes defined in `index.css`:

**Gradient Text**
```css
.gradient-text {
  @apply bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600;
}
```

**Glass Morphism**
```css
.glass {
  @apply bg-white bg-opacity-80 backdrop-blur-lg border border-gray-200;
}
```

**Slow Pulse Animation**
```css
.animate-pulse-slow {
  animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### Color Palette

- **Primary**: Blue-600 to Purple-600 (gradient)
- **Success**: Green-500
- **Warning**: Yellow-500
- **Error**: Red-500
- **Background**: Gray-50
- **Glass**: White with opacity + blur

## Integration with ShipFast

The UI communicates with ShipFast Python backend via:

1. **Spawn Process**: Backend spawns `shipfast.py`
2. **Parse Output**: Parses stdout for progress
3. **WebSocket Broadcast**: Sends updates to connected clients
4. **File Access**: Reads from `shipfast_output/` directory

### Progress Detection

Backend parses ShipFast output for keywords:

```javascript
const stages = [
  { name: 'Requirements', keywords: ['requirements', 'analyzing'], progress: 16 },
  { name: 'Architecture', keywords: ['architect', 'design'], progress: 33 },
  { name: 'Code', keywords: ['code', 'implement'], progress: 50 },
  { name: 'Review', keywords: ['review', 'security'], progress: 66 },
  { name: 'Integration', keywords: ['integration', 'test'], progress: 83 },
  { name: 'Deployment', keywords: ['deploy', 'terraform'], progress: 100 }
];
```

## Customization

### Change Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    }
  }
}
```

### Add New Pages

1. Create page in `client/src/pages/`
2. Add route in `App.js`:

```javascript
<Route path="/your-page" element={<YourPage />} />
```

3. Add navigation link

### Modify Backend

Edit `server.js`:

- Add new API endpoints
- Change WebSocket behavior
- Modify progress parsing

## Deployment

### Development

```bash
npm run dev
# Backend: http://localhost:5000
# Frontend: http://localhost:3000
```

### Production

**Option 1: Docker**

```dockerfile
FROM node:18

WORKDIR /app

# Copy UI
COPY ui/ .

# Install dependencies
RUN npm run install-all

# Build React app
RUN cd client && npm run build

# Expose port
EXPOSE 5000

# Start server
CMD ["npm", "start"]
```

**Option 2: VPS/Cloud**

```bash
# Build
npm run build

# Start with PM2
pm2 start server.js --name shipfast-ui

# Or use systemd service
```

### Environment Variables

Create `.env` in `ui/` directory:

```env
PORT=5000
NODE_ENV=production
```

## Troubleshooting

### Issue: "Cannot connect to server"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Restart backend
cd ui
npm run server
```

### Issue: "WebSocket connection failed"

**Solution:**
- Check firewall settings
- Ensure port 5000 is open
- Use correct WebSocket URL (ws:// not https://)

### Issue: "Jobs not showing"

**Solution:**
```bash
# Check ShipFast output directory
ls ../shipfast_output/

# Check backend logs
tail -f logs/server.log
```

### Issue: "Frontend won't start"

**Solution:**
```bash
# Clear cache and reinstall
cd client
rm -rf node_modules package-lock.json
npm install
npm start
```

## Performance

### Optimization Tips

1. **Enable Caching**
   - Add service worker
   - Cache static assets

2. **Lazy Loading**
   - Use React.lazy() for routes
   - Load components on demand

3. **WebSocket Connection Pooling**
   - Reuse connections
   - Implement reconnection logic

4. **File Downloads**
   - Stream large files
   - Implement pagination

## Security

### Best Practices

1. **Authentication** (TODO)
   - Add user authentication
   - Secure WebSocket connections

2. **Rate Limiting**
   - Limit API requests
   - Prevent abuse

3. **Input Validation**
   - Sanitize feature requests
   - Validate file paths

4. **CORS**
   - Configure allowed origins
   - Restrict cross-origin requests

## Future Enhancements

### Planned Features

- [ ] User authentication & accounts
- [ ] Dark mode toggle
- [ ] Code editor with syntax highlighting
- [ ] Diff viewer for generated files
- [ ] Team collaboration features
- [ ] Cost estimation per feature
- [ ] Analytics dashboard
- [ ] Mobile app (React Native)
- [ ] VS Code extension

### UI Improvements

- [ ] Drag-and-drop file upload
- [ ] Inline code editing
- [ ] Terminal emulator for deployment
- [ ] Real-time collaboration
- [ ] Notification system

## Contributing

### Development Workflow

1. Make changes in `client/src/`
2. Test locally with `npm run dev`
3. Build with `npm run build`
4. Test production with `npm start`

### Code Style

- Use functional React components
- Follow Tailwind CSS conventions
- Keep components small and focused
- Add PropTypes for type checking

## Support

### Resources

- Main ShipFast docs: `../README.md`
- API reference: See "Backend API" section
- Component examples: See `client/src/pages/`

### Getting Help

1. Check console for errors
2. Review backend logs
3. Test API endpoints with curl
4. Check WebSocket connection

---

## Summary

✅ **Modern Web UI** for ShipFast
✅ **Real-time updates** via WebSocket
✅ **5 main pages** (Home, Ship, Jobs, Job Detail, Docs)
✅ **REST API** + WebSocket backend
✅ **Responsive design** with Tailwind CSS
✅ **Production-ready** with build scripts

**Access at:** http://localhost:3000 (dev) or http://localhost:5000 (prod)

**Ship features from your browser!** 🚀
