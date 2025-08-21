# Orchestration Tools

This directory contains workflow orchestration tools and integrations for automating complex business processes.

## 🚀 Available Tools

### n8n Workflow Automation

**n8n-deployment/** - Production-ready n8n deployment
- Docker Compose setup for production
- Persistent data storage
- Environment configuration

**n8n-embedded/** - Embedded n8n for development
- Lightweight development setup
- Quick testing and prototyping

**n8n_workflow_app.py** - Streamlit app for n8n integration
- Visual workflow management
- Campaign-based workflow organization
- Integration with call center application

**test_n8n_api.py** - n8n API testing utilities
- API connection testing
- Workflow execution testing
- Development utilities

## 🔧 Setup Instructions

### 1. Production Deployment
```bash
cd agent_tools/orchestration/n8n-deployment
docker-compose up -d
```

### 2. Development Setup
```bash
cd agent_tools/orchestration/n8n-embedded
docker-compose up -d
```

### 3. Streamlit Integration
```bash
streamlit run agent_tools/orchestration/n8n_workflow_app.py
```

## 📊 Features

- **Campaign Management** - Organize workflows by campaign
- **API Integration** - Connect with Perplexity, Snowflake, and other services
- **Visual Workflow Builder** - Drag-and-drop workflow creation
- **Data Pipeline Automation** - Automated data processing and enrichment
- **Multi-step Research Flows** - Complex research and analysis workflows

## 🔗 Integration Points

- **Perplexity API** - AI-powered research and analysis
- **Snowflake Cortex** - Data warehouse and analytics
- **Google Sheets** - Data output and reporting
- **Call Center App** - Main application integration

## 📋 Workflow Templates

Common workflow patterns available:
- Company research and enrichment
- Competitive analysis automation
- Data validation and cleansing
- Multi-source data aggregation
- Automated reporting pipelines

## 🛠️ Development

When creating new workflows:
1. Use the n8n visual editor
2. Test with development setup first
3. Export workflows as JSON
4. Document workflow purpose and inputs
5. Deploy to production environment

## 🔐 Security

- Environment variables for API keys
- Secure credential storage
- Network isolation in Docker
- Regular security updates

## 📖 Documentation

Each subdirectory contains specific documentation for setup and usage. Refer to individual README files for detailed instructions.
