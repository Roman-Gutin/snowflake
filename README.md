# Call Center Application

A comprehensive call center application built with Streamlit, featuring company research, campaign management, data analytics, and workflow orchestration capabilities.

## 🏗️ Repository Structure

```
├── gsuite/
│   └── gsheets_crud/          # Google Sheets integration for Snowflake
├── orchestration/
│   └── n8n/                   # n8n workflow automation platform
├── campaigns/                 # Campaign data and configurations
├── data/                      # Application data storage
├── local-files/              # Local file storage
└── venv/                     # Python virtual environment
```

## 🚀 Key Features

### Google Sheets Integration (`gsuite/gsheets_crud/`)
- **Snowpark UDF Integration**: Write data from Snowflake directly to Google Sheets
- **OAuth 2.0 Authentication**: Secure Google API access
- **Batch Operations**: Single row or multiple row writing
- **Error Handling**: Comprehensive error reporting

### Workflow Orchestration (`orchestration/n8n/`)
- **Visual Workflow Builder**: Drag-and-drop automation
- **Campaign Management**: Organize workflows by campaign
- **API Integrations**: Perplexity, Snowflake, Google Sheets
- **Multi-step Research**: Complex data enrichment flows

### Call Center Application
- **Company Research**: AI-powered company analysis
- **Campaign Management**: Organize and track campaigns
- **Data Analytics**: Comprehensive reporting and insights
- **Streamlit Interface**: User-friendly web application

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
