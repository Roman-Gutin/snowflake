import streamlit as st
import pandas as pd
from datetime import datetime
import json
import requests
import os
import subprocess
import time
import socket
from pathlib import Path
from prompts import get_prompt, list_prompts, get_default_prompt

# API Configuration
PERPLEXITY_API_KEY = "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"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
N8N_URL = "http://localhost:5678"
N8N_PORT = 5678

def check_port_open(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def is_n8n_running():
    """Check if n8n is running"""
    return check_port_open("localhost", N8N_PORT)

def save_research_results(campaign_name, company_name, data, file_type="research"):
    """Save research results to local folder structure"""
    try:
        # Create campaign folder structure
        base_path = Path("campaigns")
        campaign_path = base_path / campaign_name / company_name
        campaign_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_type}_{timestamp}.json"
        file_path = campaign_path / filename
        
        # Save data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    except Exception as e:
        st.error(f"Failed to save results: {e}")
        return None

# Streamlit Configuration
st.set_page_config(
    page_title="Call Center Analytics Platform",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""
if 'campaign_name' not in st.session_state:
    st.session_state.campaign_name = ""

# Clean sidebar
st.sidebar.title("📞 Call Center Analytics")

# Show connection status
if st.session_state.get('snowflake_connection'):
    st.sidebar.success("✅ Snowflake Connected")
else:
    st.sidebar.warning("⚠️ Snowflake Not Connected")

# Show n8n status
if is_n8n_running():
    st.sidebar.success("✅ n8n Running")
else:
    st.sidebar.info("⚙️ n8n Available")

# Show current campaign
if st.session_state.get('company_name'):
    st.sidebar.markdown("### 🎯 Current Campaign")
    st.sidebar.markdown(f"**Company:** {st.session_state.company_name}")
    if st.session_state.get('research_results'):
        st.sidebar.success("✅ Research Complete")
    else:
        st.sidebar.info("⏳ Research Pending")

st.sidebar.markdown("---")
st.sidebar.markdown("*Simple. Fast. Effective.*")

# Main interface
st.title("📞 Call Center Analytics Platform")
st.markdown("**Campaign = n8n Flow** | Research with Perplexity → Analyze with Snowflake Cortex")

# Simple workflow tabs
tab1, tab2 = st.tabs(["🔧 Campaign Builder", "🌐 n8n Integration"])

with tab1:
    st.markdown("### 🔧 Campaign Builder")
    st.markdown("Build your call center analytics campaign with Perplexity research and Snowflake Cortex AI")

    # Campaign Configuration
    col1, col2 = st.columns([2, 1])

    with col1:
        campaign_name = st.text_input(
            "Campaign Name:",
            placeholder="e.g., Epson_Customer_Analytics_Campaign",
            help="This will be the name of your research campaign"
        )

    with col2:
        research_depth = st.selectbox(
            "Research Depth:",
            ["Standard", "Deep Analysis", "Competitive Focus"],
            help="Choose the depth of research analysis"
        )

    # Target Company
    company_name = st.text_input(
        "Target Company:",
        placeholder="e.g., Epson Americas, JustFab, Apple Inc",
        help="Company to analyze in this campaign"
    )

    # Research Configuration
    if campaign_name and company_name:
        st.markdown("---")
        st.markdown(f"### 🔍 Research Configuration: **{campaign_name}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Perplexity Settings:**")
            perplexity_model = st.selectbox(
                "Model:",
                ["sonar-pro", "sonar", "sonar-reasoning", "sonar-reasoning-pro"],
                help="Choose Perplexity model for research"
            )
            
            max_tokens = st.number_input(
                "Max Tokens:",
                min_value=1000,
                max_value=8000,
                value=8000,
                step=500
            )
        
        with col2:
            st.markdown("**Research Sources:**")
            research_sources = st.multiselect(
                "Include Sources:",
                ["BBB.org", "PissedConsumer", "Reddit", "Trustpilot", "Google Reviews", "News"],
                default=["BBB.org", "PissedConsumer", "Reddit"]
            )
            
            include_competitive = st.checkbox(
                "Include Competitive Analysis",
                value=True,
                help="Add competitor research and market positioning"
            )

        # Prompt Configuration
        st.markdown("**Research Prompt:**")
        
        # Initialize with default prompt if not set
        if 'custom_prompt' not in st.session_state:
            st.session_state.custom_prompt = get_default_prompt()

        # Show prompt in expander
        with st.expander("📝 Edit Research Prompt", expanded=False):
            research_prompt = st.text_area(
                "Research Prompt:",
                value=st.session_state.custom_prompt,
                height=300,
                help="Edit this prompt to refine your research. Use {company_name} as placeholder."
            )
            
            # Auto-save when prompt changes
            if research_prompt != st.session_state.custom_prompt:
                st.session_state.custom_prompt = research_prompt
                st.success("✅ Prompt saved!")
            
            # Show prompt stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Characters", len(research_prompt))
            with col2:
                if st.button("🔄 Reset to Default"):
                    st.session_state.custom_prompt = get_default_prompt()
                    st.rerun()

        # Research Execution
        st.markdown("---")
        st.markdown("### 🚀 Execute Research")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Test Research", type="secondary"):
                st.session_state.company_name = company_name
                st.session_state.campaign_name = campaign_name
                
                with st.spinner(f"Testing research for {company_name}..."):
                    # Format prompt
                    try:
                        formatted_prompt = research_prompt.format(company_name=company_name)
                    except (KeyError, ValueError):
                        formatted_prompt = research_prompt.replace("{company_name}", company_name)
                    
                    # Execute research
                    headers = {
                        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    try:
                        test_data = {
                            "model": perplexity_model,
                            "messages": [{"role": "user", "content": formatted_prompt}],
                            "max_tokens": max_tokens,
                            "temperature": 0,
                            "return_citations": True,
                            "return_related_questions": True
                        }
                        
                        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=test_data, timeout=300)
                        
                        if response.status_code == 200:
                            result = response.json()
                            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                            citations = result.get('citations', [])
                            
                            # Store test results
                            st.session_state.test_results = {
                                'content': content,
                                'citations': citations,
                                'model_used': perplexity_model,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            st.success("✅ Test research completed!")
                            st.rerun()
                        else:
                            st.error(f"❌ API Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error during research: {str(e)}")
        
        with col2:
            if st.button("🚀 Run Full Campaign", type="primary"):
                st.session_state.company_name = company_name
                st.session_state.campaign_name = campaign_name
                
                with st.spinner(f"Running full campaign for {company_name}..."):
                    # Execute full research workflow
                    st.success("✅ Campaign executed! (Full implementation would run here)")
                    st.info("This would execute the complete research → analysis → Snowflake pipeline")

with tab2:
    st.markdown("### 🌐 n8n Integration")
    st.markdown("Connect your campaigns to n8n for visual workflow automation")
    
    # n8n Status Check
    n8n_running = is_n8n_running()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("n8n Status", "🟢 Running" if n8n_running else "🔴 Not Running")
    
    with col2:
        st.metric("URL", N8N_URL if n8n_running else "Not Available")
    
    with col3:
        if n8n_running:
            if st.button("🌐 Open n8n"):
                st.markdown(f"**Opening n8n:** {N8N_URL}")
                st.markdown(f"[Click here to open n8n]({N8N_URL})")
        else:
            st.info("Start n8n separately")
    
    st.markdown("---")
    
    if n8n_running:
        st.success("✅ n8n is running! You can build visual workflows.")
        
        # Quick setup guide
        st.markdown("### 🔧 Quick Setup in n8n")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1. Perplexity Node Setup:**")
            st.code(f"""
URL: {PERPLEXITY_API_URL}
Method: POST
Headers:
  Authorization: Bearer {PERPLEXITY_API_KEY}
            """)
        
        with col2:
            st.markdown("**2. Snowflake Node Setup:**")
            st.code("""
Account: ZWB79581
User: CALL_CENTER_SERVICE_ACCOUNT
Role: CALL_CENTER_ROLE
Auth: Key Pair
            """)
    
    else:
        st.warning("⚠️ n8n is not running")
        st.markdown("### 🚀 Start n8n Separately")
        st.markdown("""
        To start n8n in a separate terminal/app:
        
        **Option 1: Docker (Recommended)**
        ```bash
        docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
        ```
        
        **Option 2: npm**
        ```bash
        npm install n8n -g
        n8n start
        ```
        
        Then refresh this page to see the integration options.
        """)

# Show test results if available
if st.session_state.get('test_results'):
    st.markdown("---")
    st.markdown("## 🧪 Test Results")
    
    test_results = st.session_state.test_results
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"**Model Used:** {test_results.get('model_used', 'Unknown')}")
    
    with col2:
        if st.button("🗑️ Clear Results"):
            del st.session_state.test_results
            st.rerun()
    
    # Test response
    with st.expander("📄 Research Results", expanded=True):
        test_content = test_results.get('content', '')
        if test_content:
            st.markdown(test_content)
            
            # Try to extract and validate JSON
            if st.button("🎯 Extract Use Cases JSON"):
                try:
                    import re
                    
                    # Look for JSON blocks in the content
                    json_pattern = r'```json\s*(.*?)\s*```'
                    json_matches = re.findall(json_pattern, test_content, re.DOTALL)
                    
                    if json_matches:
                        try:
                            parsed_json = json.loads(json_matches[0])
                            st.success("✅ Valid JSON found!")
                            st.json(parsed_json)
                            
                            # Save extracted data
                            if st.session_state.get('campaign_name') and st.session_state.get('company_name'):
                                saved_path = save_research_results(
                                    st.session_state.campaign_name, 
                                    st.session_state.company_name, 
                                    parsed_json, 
                                    "extracted_use_cases"
                                )
                                if saved_path:
                                    st.info(f"💾 Saved to: {saved_path}")
                            
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")
                    else:
                        st.warning("⚠️ No JSON structure found in the response.")
                        
                except Exception as e:
                    st.error(f"Error extracting JSON: {str(e)}")
        else:
            st.info("No test content available.")

# Show saved campaigns
campaigns_path = Path("campaigns")
if campaigns_path.exists():
    campaigns = [d for d in campaigns_path.iterdir() if d.is_dir()]
    if campaigns:
        st.markdown("---")
        st.markdown("### 📁 Saved Campaigns")
        
        for campaign_dir in campaigns[:5]:  # Show first 5
            companies = [d for d in campaign_dir.iterdir() if d.is_dir()]
            if companies:
                with st.expander(f"📊 {campaign_dir.name}", expanded=False):
                    for company_dir in companies:
                        files = list(company_dir.glob("*.json"))
                        st.markdown(f"**{company_dir.name}** - {len(files)} files")
