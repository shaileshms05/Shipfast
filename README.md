# ShipFast - AI-Powered Development Automation Platform

**Multi-Agent AI System for Complete Software Development Lifecycle**

## 🚀 Quick Start

ShipFast v3.0 is located in the `shipfast_v3/` directory.

```bash
# Start the backend
cd shipfast_v3
./start.sh

# In a new terminal, start the frontend
cd ui/client
npm install
npm start
```

Then open http://localhost:3000 in your browser.

## 📚 Documentation

All documentation is in the `shipfast_v3/` directory:

- **[shipfast_v3/README.md](shipfast_v3/README.md)** - Complete project documentation
- **[shipfast_v3/QUICK_START.md](shipfast_v3/QUICK_START.md)** - 5-minute setup guide
- **[shipfast_v3/V3_SUMMARY.md](shipfast_v3/V3_SUMMARY.md)** - Technical summary
- **[shipfast_v3/COMPLETE.md](shipfast_v3/COMPLETE.md)** - Completion report

## 🎯 What is ShipFast?

ShipFast is an AI-powered platform that automates the entire software development lifecycle using specialized AI agents.

### ShipFast Core (6 AI Agents)
Transforms feature requests into production-ready code:
1. **Requirements Agent** - Analyzes and generates specifications
2. **Architect Agent** - Designs system architecture
3. **Code Agent** - Generates production code
4. **Review Agent** - Security and quality review
5. **Integration Agent** - Tests and documentation
6. **Deployment Agent** - Infrastructure as code

### ShipFast Deploy (4 AI Agents)
Intelligently analyzes and deploys code:
1. **Analyzer Agent** - Codebase analysis
2. **Security Agent** - Security scanning
3. **Configurator Agent** - Interactive configuration
4. **Provisioner Agent** - Infrastructure provisioning

## 🏗️ Project Structure

```
.
├── shipfast_v3/           # Main ShipFast v3.0 system
│   ├── api/              # FastAPI backend
│   ├── agents/           # All 10 AI agents
│   ├── core/             # Core system (config, state, orchestrator)
│   ├── services/         # External services (AI client)
│   ├── config/           # Configuration files
│   └── [docs]            # Comprehensive documentation
├── ui/                   # React frontend
│   └── client/           # React app
├── test_deploy/          # Test projects for deployment
├── venv/                 # Python virtual environment (old, v3 has its own)
└── README.md            # This file
```

## ✨ Key Features

- **No LangChain** - Direct Cerebras SDK integration for reliability
- **Unified Architecture** - Single orchestrator managing all workflows
- **Type-Safe** - Pydantic models throughout
- **Production-Ready** - Comprehensive error handling and logging
- **Well-Documented** - Complete guides and API docs

## 🎓 Hackathon Project

This project was built for a hackathon, showcasing:
- Multi-agent AI coordination
- End-to-end automation
- Intelligent code analysis
- Automated deployment
- Clean, production-ready architecture

## 📖 Getting Started

1. **Prerequisites**: Python 3.9+, Node.js 16+, Cerebras API key
2. **Setup**: Follow [shipfast_v3/QUICK_START.md](shipfast_v3/QUICK_START.md)
3. **Try It**: Submit a feature request at http://localhost:3000/ship

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- **Cerebras Cloud** - Fast AI inference
- **FastAPI** - Python web framework
- **React** - Frontend framework
- **Pydantic** - Data validation

---

**For complete documentation, see [shipfast_v3/README.md](shipfast_v3/README.md)**
# Shipfast
