# Agent Tools

This directory contains various tools and integrations for AI agents and automation workflows.

## 📁 Directory Structure

```
agent_tools/
├── gsuite/
│   └── gsheets_crud/
│       ├── google_sheets_handler.py
│       ├── setup_google_sheets.sql
│       └── README.md
├── orchestration/
│   ├── n8n-deployment/
│   ├── n8n-embedded/
│   ├── n8n_workflow_app.py
│   ├── test_n8n_api.py
│   └── README.md
└── README.md
```

## 🔧 Available Tools

### Google Sheets Integration (`gsuite/gsheets_crud/`)

Complete Snowpark UDF integration for writing data from Snowflake to Google Sheets.

**Features:**
- Single row writing to Google Sheets
- Batch writing for multiple rows
- OAuth 2.0 authentication
- External access integration
- Error handling and logging

**Usage:**
```sql
-- Write a single row
SELECT WRITE_TO_GOOGLE_SHEETS(
    'spreadsheet_id',
    'Sheet1',
    ['Name', 'Email', 'Date', 'Amount']
);

-- Use simplified wrapper
SELECT APPEND_ROW_TO_SHEET(
    'spreadsheet_id',
    'Sheet1',
    'John Doe',
    'john@email.com',
    '2024-01-01',
    '100.50'
);
```

### Workflow Orchestration (`orchestration/`)

Complete n8n workflow automation platform for complex business processes.

**Features:**
- Visual workflow builder
- Campaign-based organization
- API integrations (Perplexity, Snowflake)
- Multi-step research automation
- Data pipeline orchestration

**Usage:**
```bash
# Production deployment
cd agent_tools/orchestration/n8n-deployment
docker-compose up -d

# Development setup
cd agent_tools/orchestration/n8n-embedded
docker-compose up -d
```

## 🚀 Getting Started

1. **Sync Repository in Snowflake:**
   ```sql
   USE ROLE SYSADMIN;
   ALTER GIT REPOSITORY ASPECT.PUBLIC.SNOWFLAKE_REPO FETCH;
   ```

2. **Set up Google Sheets Integration:**
   - Copy `agent_tools/gsuite/gsheets_crud/setup_google_sheets.sql`
   - Update with your Google OAuth credentials
   - Run in Snowflake console

3. **Deploy n8n Orchestration:**
   - Choose production or development setup
   - Run Docker Compose commands
   - Access n8n web interface

4. **Test the Integration:**
   - Use examples from the README files

## 📋 Prerequisites

- Snowflake account with ACCOUNTADMIN access
- Google Cloud Console project with Sheets API enabled
- OAuth 2.0 credentials (Client ID, Client Secret, Refresh Token)
- Git repository integration set up in Snowflake
- Docker and Docker Compose for n8n

## 🔐 Security Notes

- OAuth credentials are stored as Snowflake secrets
- External access is limited to Google APIs only
- Never commit actual credentials to git
- Use service accounts for production deployments
- n8n credentials stored in Docker volumes

## 🎯 Future Tools

This directory is designed to be expanded with additional agent tools:

- **Slack Integration** - Send messages and notifications
- **Email Automation** - SMTP/API email sending
- **Database Connectors** - Connect to various databases
- **File Processing** - PDF, CSV, JSON processing tools
- **API Integrations** - REST API clients and webhooks
- **ML/AI Tools** - Model deployment and inference
- **Monitoring** - System and workflow monitoring

## 📖 Documentation

Each tool directory contains its own README with detailed setup instructions, usage examples, and troubleshooting guides.

## 🤝 Contributing

When adding new tools:
1. Create a descriptive directory structure
2. Include comprehensive documentation
3. Provide setup and test scripts
4. Follow security best practices
5. Update this main README
