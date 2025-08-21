import streamlit as st
import requests
import json
from datetime import datetime
from pathlib import Path

# n8n Configuration
N8N_BASE_URL = "http://localhost:5678/api/v1"
N8N_WEBHOOK_BASE = "http://localhost:5678/webhook"
N8N_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmZDhlYzIzNS01ZTQyLTQwZjMtYTUzNS1mMDU2MjBmNjdlNzEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU1NTU0NTcyfQ.JFyUPmCMbg8TKZtREv94g4UZh1iJopmpFV6kXq-4Fnw"

# Page Configuration
st.set_page_config(
    page_title="n8n Workflow Builder",
    page_icon="🔄",
    layout="wide"
)

def create_n8n_workflow(workflow_name, company_name, perplexity_prompt):
    """Create a workflow in n8n using the API"""
    
    # Define the workflow structure
    workflow_data = {
        "name": workflow_name,
        "active": True,
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": f"research-{company_name.lower().replace(' ', '-')}",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "id": "webhook-trigger",
                "name": "Company Research Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": f"research-{company_name.lower().replace(' ', '-')}"
            },
            {
                "parameters": {
                    "url": "https://api.perplexity.ai/chat/completions",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "method": "POST",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "sendBody": True,
                    "contentType": "json",
                    "jsonParameters": True,
                    "parametersJson": json.dumps({
                        "model": "sonar-pro",
                        "messages": [
                            {
                                "role": "user",
                                "content": perplexity_prompt.replace("{company_name}", "={{ $json.company_name }}")
                            }
                        ],
                        "max_tokens": 8000,
                        "temperature": 0,
                        "return_citations": True
                    }),
                    "options": {}
                },
                "id": "perplexity-research",
                "name": "Perplexity Research",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                },
                "id": "respond-webhook",
                "name": "Return Results",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300]
            }
        ],
        "connections": {
            "Company Research Trigger": {
                "main": [
                    [
                        {
                            "node": "Perplexity Research",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Perplexity Research": {
                "main": [
                    [
                        {
                            "node": "Return Results",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "staticData": None,
        "tags": [],
        "triggerCount": 1,
        "updatedAt": datetime.now().isoformat(),
        "versionId": "1"
    }
    
    return workflow_data

def call_n8n_api(endpoint, method="GET", data=None, headers=None):
    """Make API calls to n8n with authentication"""
    url = f"{N8N_BASE_URL}{endpoint}"

    default_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {N8N_API_TOKEN}"
    }

    if headers:
        default_headers.update(headers)

    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers)
        elif method == "POST":
            response = requests.post(url, headers=default_headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=default_headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=default_headers)

        return response
    except Exception as e:
        st.error(f"API call failed: {str(e)}")
        return None

def trigger_workflow_webhook(webhook_path, company_data):
    """Trigger a workflow via webhook"""
    webhook_url = f"{N8N_WEBHOOK_BASE}/{webhook_path}"
    
    try:
        response = requests.post(webhook_url, json=company_data, timeout=30)
        return response
    except Exception as e:
        st.error(f"Webhook trigger failed: {str(e)}")
        return None

# Main App Interface
st.title("🔄 n8n Workflow Builder")
st.markdown("**Create and trigger n8n workflows programmatically**")

# Sidebar for n8n status
with st.sidebar:
    st.markdown("### 🔧 n8n Status")
    
    # Check n8n connection
    try:
        health_response = call_n8n_api("/workflows")
        if health_response and health_response.status_code == 200:
            st.success("✅ n8n Connected")
            workflows_count = len(health_response.json().get('data', []))
            st.metric("Workflows", workflows_count)
        else:
            st.error("❌ n8n Not Connected")
            st.info("Make sure n8n is running on localhost:5678")
    except:
        st.error("❌ n8n Not Available")

# Main interface
tab1, tab2, tab3 = st.tabs(["🏗️ Create Workflow", "🚀 Trigger Workflow", "📊 Manage Workflows"])

with tab1:
    st.markdown("### 🏗️ Create n8n Workflow")
    st.markdown("Build a workflow that takes a company name and researches it using Perplexity")
    
    # Workflow configuration
    col1, col2 = st.columns(2)
    
    with col1:
        workflow_name = st.text_input(
            "Workflow Name:",
            value="Company Research Flow",
            help="Name for your n8n workflow"
        )
        
        company_example = st.text_input(
            "Example Company:",
            value="Apple Inc",
            help="Example company for webhook path generation"
        )
    
    with col2:
        st.markdown("**Workflow Structure:**")
        st.markdown("1. **Webhook Trigger** - Receives company name")
        st.markdown("2. **Perplexity API** - Researches the company")
        st.markdown("3. **Return Results** - Sends back research data")
    
    # Perplexity prompt configuration
    st.markdown("**Research Prompt:**")
    default_prompt = """Research {company_name} and provide:
1. Company overview and business model
2. Key products/services
3. Recent news and developments
4. Call center analytics opportunities
5. Potential use cases for customer service optimization

Format the response as structured JSON with clear sections."""
    
    perplexity_prompt = st.text_area(
        "Perplexity Prompt:",
        value=default_prompt,
        height=150,
        help="Use {company_name} as placeholder"
    )
    
    # Create workflow button
    if st.button("🔨 Create Workflow in n8n", type="primary"):
        if workflow_name and company_example and perplexity_prompt:
            with st.spinner("Creating workflow in n8n..."):
                # Create workflow data
                workflow_data = create_n8n_workflow(workflow_name, company_example, perplexity_prompt)
                
                # Call n8n API to create workflow
                response = call_n8n_api("/workflows", method="POST", data=workflow_data)
                
                if response and response.status_code in [200, 201]:
                    workflow_result = response.json()
                    workflow_id = workflow_result.get('data', {}).get('id')
                    
                    st.success(f"✅ Workflow created successfully!")
                    st.info(f"**Workflow ID:** {workflow_id}")
                    
                    # Generate webhook URL
                    webhook_path = f"research-{company_example.lower().replace(' ', '-')}"
                    webhook_url = f"{N8N_WEBHOOK_BASE}/{webhook_path}"
                    
                    st.markdown("### 🔗 Webhook Details")
                    st.code(f"POST {webhook_url}")
                    st.markdown("**Payload Example:**")
                    st.code(json.dumps({"company_name": company_example}, indent=2))
                    
                    # Store workflow info in session
                    if 'created_workflows' not in st.session_state:
                        st.session_state.created_workflows = []
                    
                    st.session_state.created_workflows.append({
                        'id': workflow_id,
                        'name': workflow_name,
                        'webhook_path': webhook_path,
                        'webhook_url': webhook_url,
                        'created_at': datetime.now().isoformat()
                    })
                    
                else:
                    st.error(f"❌ Failed to create workflow")
                    if response:
                        st.error(f"Status: {response.status_code}")
                        st.error(f"Response: {response.text}")
        else:
            st.error("Please fill in all required fields")

with tab2:
    st.markdown("### 🚀 Trigger Workflow")
    st.markdown("Test your created workflows by sending company data")
    
    # Show available workflows
    if 'created_workflows' in st.session_state and st.session_state.created_workflows:
        workflow_options = {wf['name']: wf for wf in st.session_state.created_workflows}
        
        selected_workflow_name = st.selectbox(
            "Select Workflow:",
            options=list(workflow_options.keys())
        )
        
        if selected_workflow_name:
            selected_workflow = workflow_options[selected_workflow_name]
            
            st.info(f"**Webhook URL:** {selected_workflow['webhook_url']}")
            
            # Company input
            company_name = st.text_input(
                "Company Name:",
                value="Tesla Inc",
                help="Company to research"
            )
            
            # Trigger workflow
            if st.button("🚀 Trigger Research", type="primary"):
                if company_name:
                    with st.spinner(f"Researching {company_name}..."):
                        # Prepare payload
                        payload = {
                            "company_name": company_name,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Trigger webhook
                        response = trigger_workflow_webhook(selected_workflow['webhook_path'], payload)
                        
                        if response and response.status_code == 200:
                            st.success("✅ Research completed!")
                            
                            try:
                                result_data = response.json()
                                st.markdown("### 📊 Research Results")
                                st.json(result_data)
                                
                                # Save results
                                results_path = Path("research_results")
                                results_path.mkdir(exist_ok=True)
                                
                                result_file = results_path / f"{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                with open(result_file, 'w') as f:
                                    json.dump(result_data, f, indent=2)
                                
                                st.info(f"💾 Results saved to: {result_file}")
                                
                            except json.JSONDecodeError:
                                st.warning("⚠️ Response received but not in JSON format")
                                st.text(response.text)
                        else:
                            st.error("❌ Workflow execution failed")
                            if response:
                                st.error(f"Status: {response.status_code}")
                                st.error(f"Response: {response.text}")
                else:
                    st.error("Please enter a company name")
    else:
        st.info("No workflows created yet. Create a workflow in the 'Create Workflow' tab first.")

with tab3:
    st.markdown("### 📊 Manage Workflows")
    
    # List all workflows from n8n
    if st.button("🔄 Refresh Workflows"):
        response = call_n8n_api("/workflows")
        if response and response.status_code == 200:
            workflows = response.json().get('data', [])
            st.session_state.n8n_workflows = workflows
    
    # Display workflows
    if 'n8n_workflows' in st.session_state:
        workflows = st.session_state.n8n_workflows
        
        if workflows:
            st.markdown(f"**Found {len(workflows)} workflows in n8n:**")
            
            for workflow in workflows:
                with st.expander(f"📋 {workflow.get('name', 'Unnamed')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**ID:** {workflow.get('id')}")
                        st.markdown(f"**Active:** {'✅' if workflow.get('active') else '❌'}")
                    
                    with col2:
                        st.markdown(f"**Nodes:** {len(workflow.get('nodes', []))}")
                        st.markdown(f"**Updated:** {workflow.get('updatedAt', 'Unknown')[:10]}")
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{workflow.get('id')}"):
                            delete_response = call_n8n_api(f"/workflows/{workflow.get('id')}", method="DELETE")
                            if delete_response and delete_response.status_code == 200:
                                st.success("✅ Workflow deleted")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete workflow")
        else:
            st.info("No workflows found in n8n")
    else:
        st.info("Click 'Refresh Workflows' to load workflows from n8n")

# Show created workflows in session
if 'created_workflows' in st.session_state and st.session_state.created_workflows:
    st.markdown("---")
    st.markdown("### 🎯 Recently Created Workflows")
    
    for wf in st.session_state.created_workflows:
        st.markdown(f"**{wf['name']}** - Created: {wf['created_at'][:19]}")
        st.code(f"POST {wf['webhook_url']}")
