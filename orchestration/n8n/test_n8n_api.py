#!/usr/bin/env python3
"""
Test script to verify n8n API connection and create a simple workflow
"""

import requests
import json

# Your n8n configuration
N8N_BASE_URL = "http://localhost:5678/api/v1"
N8N_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmZDhlYzIzNS01ZTQyLTQwZjMtYTUzNS1mMDU2MjBmNjdlNzEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU1NTU0NTcyfQ.JFyUPmCMbg8TKZtREv94g4UZh1iJopmpFV6kXq-4Fnw"

def test_n8n_connection():
    """Test basic n8n API connection"""
    print("🔍 Testing n8n API connection...")
    
    headers = {
        "Authorization": f"Bearer {N8N_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test basic connection by listing workflows
        response = requests.get(f"{N8N_BASE_URL}/workflows", headers=headers)
        
        if response.status_code == 200:
            workflows = response.json()
            print(f"✅ Connected to n8n successfully!")
            print(f"📊 Found {len(workflows.get('data', []))} workflows")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def create_simple_test_workflow():
    """Create a simple test workflow"""
    print("\n🏗️ Creating test workflow...")
    
    # Simple workflow with webhook trigger and response
    workflow_data = {
        "name": "Test Company Research Workflow",
        "active": True,
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "test-company-research",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "id": "webhook-trigger",
                "name": "Company Input",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300]
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
                                "content": "Research the company {{ $json.company_name }} and provide a brief overview including business model, key products, and recent developments."
                            }
                        ],
                        "max_tokens": 4000,
                        "temperature": 0,
                        "return_citations": True
                    })
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
            "Company Input": {
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
        }
    }
    
    headers = {
        "Authorization": f"Bearer {N8N_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{N8N_BASE_URL}/workflows", headers=headers, json=workflow_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('data', {}).get('id')
            print(f"✅ Workflow created successfully!")
            print(f"📋 Workflow ID: {workflow_id}")
            print(f"🔗 Webhook URL: http://localhost:5678/webhook/test-company-research")
            print("📝 Test with: curl -X POST http://localhost:5678/webhook/test-company-research -H 'Content-Type: application/json' -d '{\"company_name\": \"Apple Inc\"}'")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

def test_webhook_trigger(workflow_id=None):
    """Test triggering the webhook"""
    print("\n🚀 Testing webhook trigger...")
    
    webhook_url = "http://localhost:5678/webhook/test-company-research"
    test_data = {
        "company_name": "Tesla Inc"
    }
    
    try:
        print(f"📤 Sending request to: {webhook_url}")
        print(f"📦 Payload: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(webhook_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Webhook triggered successfully!")
            try:
                result = response.json()
                print("📊 Response received:")
                print(json.dumps(result, indent=2)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=2))
            except:
                print("📄 Response (text):")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")

if __name__ == "__main__":
    print("🔄 n8n API Test Script")
    print("=" * 50)
    
    # Test connection
    if test_n8n_connection():
        # Create test workflow
        workflow_id = create_simple_test_workflow()
        
        if workflow_id:
            # Test webhook
            test_webhook_trigger(workflow_id)
        
        print("\n" + "=" * 50)
        print("✅ Test completed!")
        print("🌐 Open your n8n interface at: http://localhost:5678")
        print("📱 Open the Streamlit app at: http://localhost:8503")
    else:
        print("\n❌ Cannot proceed - n8n connection failed")
        print("💡 Make sure:")
        print("   - n8n is running on localhost:5678")
        print("   - API is enabled in n8n settings")
        print("   - Your API token is valid")
