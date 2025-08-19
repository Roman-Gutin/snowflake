import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/company-research"
N8N_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmZDhlYzIzNS01ZTQyLTQwZjMtYTUzNS1mMDU2MjBmNjdlNzEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU1NTU0NTcyfQ.JFyUPmCMbg8TKZtREv94g4UZh1iJopmpFV6kXq-4Fnw"

# Page config
st.set_page_config(
    page_title="Company Research",
    page_icon="🔍",
    layout="centered"
)

# Simple, clean interface
st.title("🔍 Company Research")
st.markdown("**Enter a company name to trigger n8n workflow with Perplexity research**")

# Single input field
company_name = st.text_input(
    "Company Name:",
    placeholder="e.g., Apple Inc, Tesla, Microsoft",
    help="Enter the company you want to research"
)

# Research button
if st.button("🚀 Research Company", type="primary", use_container_width=True):
    if company_name.strip():
        with st.spinner(f"Researching {company_name}..."):
            try:
                # Prepare payload for n8n webhook
                payload = {
                    "company_name": company_name.strip(),
                    "timestamp": datetime.now().isoformat(),
                    "source": "streamlit_app"
                }
                
                # Trigger n8n workflow via webhook
                response = requests.post(
                    N8N_WEBHOOK_URL, 
                    json=payload, 
                    timeout=60,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    st.success(f"✅ Research completed for {company_name}!")
                    
                    try:
                        # Try to parse JSON response
                        result_data = response.json()
                        
                        # Display results
                        st.markdown("### 📊 Research Results")
                        
                        # Check if it's Perplexity API response format
                        if 'choices' in result_data and len(result_data['choices']) > 0:
                            content = result_data['choices'][0].get('message', {}).get('content', '')
                            if content:
                                st.markdown(content)
                                
                                # Show citations if available
                                if 'citations' in result_data:
                                    with st.expander("📚 Sources & Citations"):
                                        for i, citation in enumerate(result_data['citations'], 1):
                                            st.markdown(f"**{i}.** {citation}")
                            else:
                                st.json(result_data)
                        else:
                            # Display raw JSON if not Perplexity format
                            st.json(result_data)
                        
                        # Save results locally
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"research_{company_name.replace(' ', '_')}_{timestamp}.json"
                        
                        with open(filename, 'w') as f:
                            json.dump(result_data, f, indent=2)
                        
                        st.info(f"💾 Results saved to: {filename}")
                        
                    except json.JSONDecodeError:
                        # Handle non-JSON response
                        st.markdown("### 📄 Research Results")
                        st.text(response.text)
                        
                        # Save as text file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"research_{company_name.replace(' ', '_')}_{timestamp}.txt"
                        
                        with open(filename, 'w') as f:
                            f.write(response.text)
                        
                        st.info(f"💾 Results saved to: {filename}")
                
                elif response.status_code == 404:
                    st.error("❌ n8n webhook not found")
                    st.info("Make sure you have created a workflow with webhook path: 'company-research'")
                    
                elif response.status_code == 500:
                    st.error("❌ n8n workflow execution failed")
                    st.error("Check your n8n workflow for errors (Perplexity credentials, node configuration, etc.)")
                    
                else:
                    st.error(f"❌ Request failed with status {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to n8n")
                st.info("Make sure n8n is running on localhost:5678")
                
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out")
                st.info("The research is taking longer than expected. Check n8n for execution status.")
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
    else:
        st.error("Please enter a company name")

# Instructions
st.markdown("---")
st.markdown("### 🛠️ Setup Instructions")

with st.expander("📋 n8n Workflow Setup", expanded=False):
    st.markdown("""
    **1. Create n8n Workflow:**
    - Open n8n at http://localhost:5678
    - Create new workflow
    - Add **Webhook** node with path: `company-research`
    - Add **HTTP Request** node for Perplexity API
    - Connect nodes and activate workflow
    
    **2. Perplexity Node Configuration:**
    ```
    URL: https://api.perplexity.ai/chat/completions
    Method: POST
    Authentication: Use your Perplexity credentials
    Body (JSON):
    {
      "model": "sonar-pro",
      "messages": [
        {
          "role": "user",
          "content": "Research {{ $json.company_name }} and provide comprehensive analysis"
        }
      ],
      "max_tokens": 8000,
      "temperature": 0,
      "return_citations": true
    }
    ```
    
    **3. Test:**
    - Activate your workflow
    - Enter company name above
    - Click "Research Company"
    """)

with st.expander("🔧 Troubleshooting", expanded=False):
    st.markdown("""
    **Common Issues:**
    
    - **"Cannot connect to n8n"**: Make sure n8n is running on port 5678
    - **"Webhook not found"**: Check webhook path is exactly `company-research`
    - **"Workflow execution failed"**: Verify Perplexity credentials in n8n
    - **Empty results**: Check n8n execution log for errors
    
    **Quick Test:**
    ```bash
    curl -X POST http://localhost:5678/webhook/company-research \\
         -H "Content-Type: application/json" \\
         -d '{"company_name": "Apple Inc"}'
    ```
    """)

# Status indicators
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Test n8n connection
    try:
        test_response = requests.get("http://localhost:5678", timeout=2)
        if test_response.status_code in [200, 404]:  # 404 is normal for root path
            st.success("✅ n8n is running")
        else:
            st.warning("⚠️ n8n status unclear")
    except:
        st.error("❌ n8n not accessible")

with col2:
    # Show webhook URL
    st.info(f"🔗 Webhook: {N8N_WEBHOOK_URL}")

# Footer
st.markdown("---")
st.markdown("*Simple company research powered by n8n + Perplexity*")
