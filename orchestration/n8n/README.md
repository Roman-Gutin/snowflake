# n8n Workflow Orchestration

Complete n8n workflow automation platform for complex business processes and campaign management.

## 🚀 Available Tools

### n8n Deployments

**n8n-deployment/** - Production-ready n8n deployment
- Docker Compose setup for production
- Persistent data storage
- Environment configuration
- SSL/TLS support

**n8n-embedded/** - Embedded n8n for development
- Lightweight development setup
- Quick testing and prototyping
- Local development environment

### Integration Tools

**n8n_workflow_app.py** - Streamlit app for n8n integration
- Visual workflow management
- Campaign-based workflow organization
- Integration with call center application
- Workflow monitoring and execution

**test_n8n_api.py** - n8n API testing utilities
- API connection testing
- Workflow execution testing
- Development and debugging utilities

## 🔧 Setup Instructions

### 1. Production Deployment
```bash
cd orchestration/n8n/n8n-deployment
docker-compose up -d
```

Access n8n at: `http://localhost:5678`

### 2. Development Setup
```bash
cd orchestration/n8n/n8n-embedded
docker-compose up -d
```

Access n8n at: `http://localhost:5678`

### 3. Streamlit Integration
```bash
streamlit run orchestration/n8n/n8n_workflow_app.py
```

## 📊 Features

- **Campaign Management** - Organize workflows by campaign
- **API Integration** - Connect with Perplexity, Snowflake, and other services
- **Visual Workflow Builder** - Drag-and-drop workflow creation
- **Data Pipeline Automation** - Automated data processing and enrichment
- **Multi-step Research Flows** - Complex research and analysis workflows
- **Webhook Support** - Trigger workflows via HTTP webhooks
- **Scheduled Execution** - Time-based workflow triggers

## 🔗 Integration Points

- **Perplexity API** - AI-powered research and analysis
- **Snowflake Cortex** - Data warehouse and analytics
- **Google Sheets** - Data output and reporting
- **Call Center App** - Main application integration
- **REST APIs** - Connect to any HTTP-based service
- **Database Connectors** - MySQL, PostgreSQL, MongoDB support

## 📋 Workflow Templates

Common workflow patterns available:
- Company research and enrichment
- Competitive analysis automation
- Data validation and cleansing
- Multi-source data aggregation
- Automated reporting pipelines
- Lead qualification processes
- Customer data enrichment

## 🛠️ Development Workflow

When creating new workflows:
1. Use the n8n visual editor
2. Test with development setup first
3. Export workflows as JSON
4. Document workflow purpose and inputs
5. Deploy to production environment
6. Monitor execution and performance

## 🔐 Security

- Environment variables for API keys
- Secure credential storage in n8n vault
- Network isolation in Docker
- Regular security updates
- Access control and authentication

## 📖 API Documentation

### n8n REST API Endpoints

- `GET /workflows` - List all workflows
- `POST /workflows/{id}/execute` - Execute workflow
- `GET /executions` - List workflow executions
- `POST /webhooks/{path}` - Webhook triggers

### Webhook Usage
```bash
# Trigger workflow via webhook
curl -X POST http://localhost:5678/webhook/your-webhook-path \
  -H "Content-Type: application/json" \
  -d '{"data": "your-payload"}'
```

## 🚀 Getting Started

1. **Start n8n**: Choose production or development setup
2. **Access Web Interface**: Open browser to `http://localhost:5678`
3. **Create First Workflow**: Use the visual editor
4. **Test Execution**: Run workflow manually
5. **Set up Triggers**: Add webhooks or schedules
6. **Monitor Results**: Check execution logs

Happy automating! 🎯
