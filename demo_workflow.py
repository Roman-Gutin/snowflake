#!/usr/bin/env python3
"""
Demo script showing how the n8n workflow would work
"""

import requests
import json
from datetime import datetime

# Your Perplexity API key
PERPLEXITY_API_KEY = "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"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

def simulate_n8n_workflow(company_name):
    """Simulate what your n8n workflow would do"""
    print(f"🔄 Simulating n8n workflow for: {company_name}")
    print("=" * 50)
    
    # Step 1: Webhook receives company name
    print("📥 Step 1: Webhook received company data")
    webhook_data = {
        "company_name": company_name,
        "timestamp": datetime.now().isoformat(),
        "source": "streamlit_app"
    }
    print(f"   Data: {json.dumps(webhook_data, indent=2)}")
    
    # Step 2: Perplexity API call
    print("\n🔍 Step 2: Calling Perplexity API")
    
    research_prompt = f"""Research {company_name} and provide:
1. Company overview and business model
2. Key products/services  
3. Recent news and developments
4. Call center analytics opportunities
5. Potential use cases for customer service optimization

Format the response as structured information with clear sections."""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": research_prompt
            }
        ],
        "max_tokens": 8000,
        "temperature": 0,
        "return_citations": True
    }
    
    try:
        print(f"   Making API call to: {PERPLEXITY_API_URL}")
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            citations = result.get('citations', [])
            
            print("✅ Step 2: Perplexity API call successful!")
            print(f"   Response length: {len(content)} characters")
            print(f"   Citations: {len(citations)} sources")
            
            # Step 3: Return results (what n8n would do)
            print("\n📤 Step 3: Returning results to Streamlit app")
            
            final_result = {
                "company_name": company_name,
                "research_content": content,
                "citations": citations,
                "timestamp": datetime.now().isoformat(),
                "model_used": "sonar-pro",
                "workflow_status": "completed"
            }
            
            # Save results (simulate what the app would do)
            filename = f"demo_research_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(final_result, f, indent=2)
            
            print(f"💾 Results saved to: {filename}")
            
            # Display preview of results
            print("\n📊 Research Results Preview:")
            print("-" * 30)
            print(content[:500] + "..." if len(content) > 500 else content)
            
            if citations:
                print(f"\n📚 Sources ({len(citations)}):")
                for i, citation in enumerate(citations[:3], 1):
                    print(f"   {i}. {citation}")
                if len(citations) > 3:
                    print(f"   ... and {len(citations) - 3} more sources")
            
            return final_result
            
        else:
            print(f"❌ Step 2: API call failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Step 2: Error during API call: {str(e)}")
        return None

def main():
    print("🚀 n8n Workflow Demo")
    print("This simulates what happens when you enter a company name in the Streamlit app")
    print()
    
    # Test companies
    test_companies = ["Apple Inc", "Tesla", "Microsoft", "Amazon"]
    
    print("Available test companies:")
    for i, company in enumerate(test_companies, 1):
        print(f"  {i}. {company}")
    
    print("\nEnter a company name or number (1-4):")
    user_input = input("> ").strip()
    
    # Parse input
    if user_input.isdigit() and 1 <= int(user_input) <= len(test_companies):
        company_name = test_companies[int(user_input) - 1]
    elif user_input:
        company_name = user_input
    else:
        company_name = "Apple Inc"  # Default
    
    print(f"\n🎯 Selected company: {company_name}")
    print()
    
    # Run the simulation
    result = simulate_n8n_workflow(company_name)
    
    if result:
        print("\n" + "=" * 50)
        print("✅ Workflow completed successfully!")
        print("🌐 In the real app, this would appear in your browser")
        print("📱 Open http://localhost:8504 to see the actual interface")
    else:
        print("\n" + "=" * 50)
        print("❌ Workflow failed")
        print("💡 Check your Perplexity API key and internet connection")

if __name__ == "__main__":
    main()
