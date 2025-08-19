"""
Call Center Analytics Research Prompts
Single comprehensive prompt for themes/tags-based analytics
"""

# Main call center campaign prompt with themes and tags
CALL_CENTER_CAMPAIGN_PROMPT = """**PROMPT:**

Research the company **{company_name}** for call center analytics and cost/value optimization opportunities.

Call center analytics will be delivered by transcribing customer calls into timestamped transcripts, followed by LLM-powered topic and sentiment classification via **AI_CLASSIFY**, **AI_COMPLETE (Structured Outputs)**, and (as needed) **AI_AGG** in Snowflake Cortex.

---

**Your Tasks:**

1. **Surface Real-World Customer and Business Pain:**
   - Crawl and summarize complaint patterns, recurring pain points, and "reason for call" topics about **{company_name}** from:
     - BBB.org (resolution times, specific product/service friction, escalation and lost revenue risk)
     - PissedConsumer (root causes, escalation, re-contact triggers)
     - Reddit and relevant forums (live debate, technical issues, process themes, switching/competitive complaints)
     - Consumer review sites (Trustpilot, Sitejabber, Google Reviews, etc. if available) — extract main complaint/feedback themes
     - Macro news (lawsuits, regulatory events, product launches, support outages, public CX crises)
   - **Extract and list the top complaint/feedback themes** that repeat across these sources; make them product, service, or policy specific (not generic "support unhelpful").

2. **Verify and Output Core Company Contact Info:**
   - Find and validate the **official website URL**.
   - Find and validate the **call center or customer support phone number**.

3. **Document Data Enrichment Potential:**
   - At the top of the JSON output, list likely data sets the customer has for possible enrichment and integration with call analytics.

4. **Derive Deep, Creative Use Cases That Map Directly to Value for {company_name}:**
   - **Be Creative and Deep**: Go beyond basic complaint resolution. Consider advanced analytics like:
     - Cross-process agent performance analytics with 360-degree KPI views
     - Real-time sentiment prediction and dynamic call routing
     - Predictive churn modeling based on conversation patterns
     - Agent coaching automation using AI-powered quality assurance
     - Revenue optimization through upsell/cross-sell moment detection
     - Competitive intelligence from conversation mining
     - Regulatory compliance monitoring and risk flagging
     - Customer journey optimization across multiple touchpoints
     - Proactive issue prevention using predictive analytics
   - Each use case must stem from high-frequency or high-impact call types and demonstrated themes
   - Make every use case value-driven with specific business impact quantification
   - **Include at least one use case for competitive intelligence and one for predictive analytics**
   - Ensure there are **at least 20 business questions total across all use cases**
   - Each business question must include a `required_data_sets` field

5. **Create Consumable Themes and Tags Structure:**
   - **Themes**: High-level conceptual categories (e.g., "escalation language patterns", "competitor switching signals")
   - **Tags**: Specific, detectable keywords, phrases, or patterns that can be aggregated, windowed, and ratio'd to tell stories about themes (e.g., "WastingMyTime_GetManager", "CompetitorX_BetterPrice", "RefundDelay_BankDispute")
   - Tags should be specific enough that when aggregated over time windows and compared as ratios, they provide actionable insights about the theme

6. **Output the following JSON structure:**

```json
{{
  "data_customer_likely_has": [
    "CRM (customer profiles, purchase history, lifecycle stage)",
    "ERP (orders, fulfillment, inventory, refunds)",
    "Product registration/warranty database",
    "E-commerce transaction logs",
    "Customer feedback surveys/NPS scores",
    "IVR/call disposition and routing logs",
    "Marketing campaign data and attribution",
    "Agent performance metrics and scorecards",
    "Knowledge base and FAQ interaction logs",
    "Social media monitoring data",
    "Competitive pricing and feature data",
    "Financial/billing system data"
  ],
  "company_website": "company_website_url",
  "call_center_number": "company_phone_number",
  "call_center_usecases": [
    {{
      "name": "Predictive Churn Detection with Real-Time Intervention Triggers",
      "themes_to_track": [
        "escalation_language_patterns",
        "competitor_switching_signals",
        "value_proposition_questioning",
        "cancellation_exploration_behavior"
      ],
      "tags_to_track": [
        "WastingMyTime_GetManager",
        "CompetitorX_BetterPrice",
        "CancelSubscription_HowTo",
        "NotWorthTheMoney_Overpriced",
        "SwitchingTo_CompetitorY",
        "RefundRequest_Immediate",
        "UnresolvedIssue_MultipleContacts",
        "FrustrationLevel_High"
      ],
      "Value_Drivers": ["Increase Revenue", "Decrease Brand Risk"],
      "Reasoning_for_Value_Prop": "Advanced sentiment analysis combined with conversation pattern recognition can predict churn probability in real-time, triggering immediate retention actions during the call itself rather than post-call surveys. This prevents revenue loss and reduces acquisition costs.",
      "TopicsToInsight": "Machine learning models combine specific tag frequencies, temporal patterns (e.g., spike in 'WastingMyTime_GetManager' tags), and ratios (e.g., 'CompetitorX_BetterPrice' to total competitive mentions) to generate real-time churn probability scores. Integration with CRM and campaign data enables immediate targeted retention offers.",
      "Insights_Unlocked": [
        {{
          "business_question": "What specific tag combinations predict churn with highest accuracy within the first 2 minutes of a call?",
          "required_data_sets": ["call_tags", "call_timestamps", "CRM", "historical_churn_data"],
          "hypothetical_answer": "Calls with 'CompetitorX_BetterPrice' + 'NotWorthTheMoney_Overpriced' tags within 90 seconds have 78% churn probability.",
          "action_to_take": "Auto-trigger retention specialist transfer and pre-load competitive pricing match offers in agent dashboard when this tag combination appears."
        }},
        {{
          "business_question": "How do tag ratios change seasonally and affect churn prediction accuracy?",
          "required_data_sets": ["call_tags", "seasonal_data", "churn_history", "marketing_campaigns"],
          "hypothetical_answer": "During competitor sale seasons, 'CompetitorX_BetterPrice' to 'ValueProp_Satisfied' ratio increases 340%, improving churn prediction accuracy by 23%.",
          "action_to_take": "Adjust retention offer algorithms and agent scripts during competitor campaign periods based on tag ratio thresholds."
        }},
        {{
          "business_question": "Which high-value customer segments show specific tag patterns that predict churn before traditional metrics?",
          "required_data_sets": ["call_tags", "CRM", "customer_lifetime_value", "engagement_metrics"],
          "hypothetical_answer": "Enterprise customers with increasing 'UnresolvedIssue_MultipleContacts' tags but stable usage show 45% churn risk within 60 days.",
          "action_to_take": "Deploy proactive account management outreach when 'UnresolvedIssue_MultipleContacts' tag frequency exceeds 2x baseline for enterprise accounts."
        }},
        {{
          "business_question": "How do agent conversation tags influence customer retention likelihood?",
          "required_data_sets": ["call_tags", "agent_performance", "customer_retention", "agent_actions"],
          "hypothetical_answer": "When agents respond to 'FrustrationLevel_High' tags with 'EmpathyResponse_Immediate' within 30 seconds, retention improves by 31%.",
          "action_to_take": "Implement real-time tag-based conversation coaching that prompts agents with specific responses when churn-risk tags appear."
        }}
      ],
      "ROI_Summary": "Preventing just 2% of predicted churn through real-time tag-based interventions could save $3.2M annually in customer acquisition costs while preserving $8.1M in at-risk revenue."
    }},
    {{
      "name": "AI-Powered Cross-Process Agent Performance Optimization with Dynamic Coaching",
      "themes_to_track": [
        "resolution_efficiency_patterns",
        "customer_satisfaction_indicators",
        "upsell_opportunity_recognition",
        "compliance_adherence_markers"
      ],
      "tags_to_track": [
        "FirstCallResolution_Success",
        "UpsellMoment_Identified",
        "CustomerSatisfied_Verbal",
        "ComplianceCheck_Completed",
        "TechnicalKnowledge_Gap",
        "SolutionOffered_Specific",
        "FollowUpPromised_Timeline",
        "EscalationAvoided_DeEscalation"
      ],
      "Value_Drivers": ["Decrease Cost", "Increase Revenue"],
      "Reasoning_for_Value_Prop": "Real-time analysis of agent conversation tags across all processes creates 360-degree performance insights, enabling dynamic coaching, optimized call routing, and identification of high-performing techniques that can be scaled across the team.",
      "TopicsToInsight": "Advanced tag frequency analysis and ratios (e.g., 'UpsellMoment_Identified' to 'UpsellMoment_Converted') across agents and call types identify top-performing conversation techniques. Time-windowed tag analysis reveals performance patterns and coaching opportunities.",
      "Insights_Unlocked": [
        {{
          "business_question": "Which specific tag combinations correlate with highest first-call resolution rates across different call types?",
          "required_data_sets": ["call_tags", "agent_performance", "resolution_outcomes", "call_types"],
          "hypothetical_answer": "Agents with 'SolutionOffered_Specific' + 'FollowUpPromised_Timeline' tags achieve 34% higher first-call resolution across technical support calls.",
          "action_to_take": "Implement real-time tag-based conversation guidance that prompts agents to offer specific solutions and timelines for technical calls."
        }},
        {{
          "business_question": "How do agent tag ratios affect upsell success rates and customer satisfaction simultaneously?",
          "required_data_sets": ["call_tags", "sales_outcomes", "satisfaction_scores", "agent_metrics"],
          "hypothetical_answer": "Agents with 'UpsellMoment_Identified' to 'CustomerSatisfied_Verbal' ratio above 0.7 achieve 67% higher upsell rates with 23% higher satisfaction.",
          "action_to_take": "Train agents to ensure customer satisfaction signals before presenting upsell opportunities, using tag ratio monitoring for performance tracking."
        }},
        {{
          "business_question": "Which agents show specific tag patterns indicating need for targeted coaching interventions?",
          "required_data_sets": ["call_tags", "agent_performance", "training_history", "customer_outcomes"],
          "hypothetical_answer": "15 agents consistently show 'TechnicalKnowledge_Gap' tags without corresponding 'SolutionOffered_Specific' tags during technical calls.",
          "action_to_take": "Deploy targeted technical training for identified agents and create real-time knowledge base prompts when 'TechnicalKnowledge_Gap' tags appear."
        }}
      ],
      "ROI_Summary": "Optimizing agent performance through AI tag-based coaching could improve first-call resolution by 15%, saving $1.8M in labor costs while increasing upsell revenue by $2.4M annually."
    }},
    {{
      "name": "Competitive Intelligence and Market Position Monitoring",
      "themes_to_track": [
        "competitor_product_comparisons",
        "pricing_sensitivity_discussions",
        "feature_gap_mentions",
        "switching_triggers_and_timelines"
      ],
      "tags_to_track": [
        "CompetitorA_PricingBetter",
        "CompetitorB_FeatureAdvantage",
        "CompetitorC_ServiceSuperior",
        "SwitchingTimeline_30Days",
        "PriceMatch_Requested",
        "FeatureRequest_CompetitorHas",
        "ContractEnd_ConsideringOptions",
        "MarketResearch_ShoppingAround"
      ],
      "Value_Drivers": ["Increase Revenue", "Decrease Brand Risk"],
      "Reasoning_for_Value_Prop": "Systematic analysis of competitor-related tags, feature comparison mentions, and switching timeline indicators provides real-time market intelligence that informs product development, pricing strategies, and competitive positioning.",
      "TopicsToInsight": "Tag aggregation and windowing analysis reveal competitive pressure patterns, with ratios like 'PriceMatch_Requested' to total competitive tags indicating pricing vulnerability. Temporal analysis of competitive tags correlates with market events and campaign effectiveness.",
      "Insights_Unlocked": [
        {{
          "business_question": "Which competitor tags and tag combinations most frequently precede customer switching decisions?",
          "required_data_sets": ["call_tags", "competitor_mentions", "churn_data", "switching_outcomes"],
          "hypothetical_answer": "'CompetitorA_PricingBetter' + 'SwitchingTimeline_30Days' tag combination appears in 67% of successful competitor switches.",
          "action_to_take": "Create automated alerts when this tag combination appears and deploy immediate retention specialists with competitive pricing authority."
        }},
        {{
          "business_question": "How do competitor product launches impact our customer conversation tag patterns and market position?",
          "required_data_sets": ["call_tags", "competitive_intelligence", "product_launch_dates", "tag_frequency"],
          "hypothetical_answer": "Post-competitor launch, 'FeatureRequest_CompetitorHas' tags increased 78% while 'CustomerSatisfied_Verbal' tags dropped 23%.",
          "action_to_take": "Fast-track product development for high-frequency feature request tags and deploy feature education campaigns to highlight existing capabilities."
        }},
        {{
          "business_question": "What tag ratios indicate customers actively shopping competitors vs. passive research?",
          "required_data_sets": ["call_tags", "customer_behavior", "purchase_intent", "timeline_data"],
          "hypothetical_answer": "Customers with 'MarketResearch_ShoppingAround' to 'SwitchingTimeline_30Days' ratio above 0.5 convert to competitors at 4x baseline rate.",
          "action_to_take": "Prioritize high-ratio customers for immediate competitive retention campaigns and specialized pricing negotiations."
        }}
      ],
      "ROI_Summary": "Competitive intelligence-driven tag-based interventions could capture an additional 8% market share, representing $15M in new revenue while preventing $4.2M in competitive losses."
    }}
  ]
}}
```

---

**Instructions:**
- **Create consumable tags**: Make tags specific keywords/phrases that can be detected, counted, and analyzed over time windows (e.g., daily, weekly ratios)
- **Ensure tag aggregation value**: Tags should be designed so that when aggregated, windowed, and ratio'd, they tell clear stories about business themes and enable actionable decisions
- **Link themes to tags**: Each theme should have 3-8 corresponding specific tags that, when analyzed together, provide insights about that theme
- **Make tags business-relevant**: Focus on tags that directly connect to revenue, cost, or risk outcomes for the specific company
- **Be deeply creative**: Apply sophisticated analytical approaches using tag combinations, ratios, and temporal patterns
- **Base on real research**: Ground all themes and tags in actual complaint patterns and business realities discovered from research sources
- Include at least 20 total business questions across all use cases with required data sets specified
- Output only the JSON—fully populated, valid, ready-to-use"""

# Data Capture Strategy prompt for n8n/Perplexity integration
DATA_CAPTURE_STRATEGY_PROMPT = """Research the company: {{ $json.body.company_name }}

Based on this company's business model, industry, and operational characteristics, recommend specific data sources for capture across structured, semi-structured, and unstructured data types.

**ANALYSIS INSTRUCTIONS:**

1. Research the company's industry, business model, and operational characteristics
2. Identify specific data sources that would be valuable for this company
3. Focus on actionable business intelligence opportunities
4. Provide clear reasoning for why each data source creates business value

**OUTPUT ONLY THIS JSON - NO OTHER TEXT:**

```json
{
  "company_verification": {
    "website": "official_website_url",
    "business_model": "brief_description_of_primary_business",
    "industry": "primary_industry_classification"
  },
  "structured_data": [
    "transaction_records",
    "customer_profiles",
    "inventory_levels",
    "call_center_metrics",
    "financial_data"
  ],
  "structured_data_reasoning": "Structured data sources like transaction records enable real-time revenue tracking and customer lifetime value calculations. Customer profiles support personalized marketing and retention strategies. Inventory levels prevent stockouts and optimize supply chain. Call center metrics identify agent performance patterns and customer satisfaction drivers. Financial data enables predictive budgeting and cost optimization.",
  "semi_structured_data": [
    "email_threads",
    "support_tickets",
    "survey_responses",
    "social_media_posts",
    "api_logs"
  ],
  "semi_structured_data_reasoning": "Email threads reveal customer pain points and resolution patterns for process improvement. Support tickets identify recurring issues and knowledge gaps. Survey responses provide direct customer feedback for product development. Social media posts capture brand sentiment and competitive intelligence. API logs track system performance and integration health for operational optimization.",
  "unstructured_data": [
    "call_recordings",
    "product_manuals",
    "customer_reviews",
    "video_content",
    "chat_transcripts"
  ],
  "unstructured_data_reasoning": "Call recordings provide deep sentiment analysis and conversation intelligence for agent coaching and customer experience optimization. Product manuals contain knowledge that can be mined for FAQ automation and support efficiency. Customer reviews reveal product improvement opportunities and competitive positioning insights. Video content engagement patterns inform marketing strategy and content optimization. Chat transcripts enable real-time intent detection and automated response improvements."
}
```

CRITICAL REQUIREMENTS:
- Output ONLY the JSON structure above, no additional text
- Include exactly 5 data sources for each category
- Make data sources specific to the company's industry and business model
- Ensure reasoning explains concrete business value and actionable intelligence
- Use realistic data sources the company would actually have access to
- Focus on sources that drive revenue, reduce costs, or mitigate risks"""

# Prompt templates dictionary
PROMPT_TEMPLATES = {
    "call_center_campaign": CALL_CENTER_CAMPAIGN_PROMPT,
    "data_capture_strategy": DATA_CAPTURE_STRATEGY_PROMPT
}

def get_prompt(template_name: str = "call_center_campaign") -> str:
    """Get a prompt template by name"""
    return PROMPT_TEMPLATES.get(template_name, CALL_CENTER_CAMPAIGN_PROMPT)

def list_prompts() -> list:
    """List available prompt templates"""
    return list(PROMPT_TEMPLATES.keys())

def get_default_prompt() -> str:
    """Get the default call center campaign prompt"""
    return CALL_CENTER_CAMPAIGN_PROMPT
