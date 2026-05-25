"""
Action Center module for AI-assisted campaign planning.

Turns analytics outputs into actionable retention campaign plans.
"""

from llm_client import chat_completion

CAMPAIGN_SESSION_KEYS = (
    "campaign_plan",
    "campaign_metrics",
    "campaign_users_df",
    "campaign_target_segment",
    "execution_recommendations",
)

EXECUTION_RECOMMENDATIONS = {
    "High-value Churn-risk User": [
        "Email campaign with exclusive retention offers",
        "VIP retention concierge outreach",
        "Personalized high-value win-back discounts",
        "Loyalty rewards for repeat purchase",
    ],
    "High-potential User": [
        "Reactivation push notification with limited-time offer",
        "Personalized product recommendations",
        "Cart recovery email sequence",
        "First-purchase incentive campaign",
    ],
    "Silent User": [
        "Low-cost reactivation email campaign",
        "Push notification reminder campaign",
        "Lightweight engagement survey offer",
        "Welcome-back coupon campaign",
    ],
    "default": [
        "Email campaign with seasonal promotion",
        "Personalized offers based on browsing history",
        "Loyalty rewards program enrollment",
        "Cross-sell recommendation campaign",
    ],
}


def get_retention_target_segment(segment_counts):
    """Pick the best segment to focus a retention campaign on."""
    if segment_counts.get("High-value Churn-risk User", 0) > 100:
        return "High-value Churn-risk User"
    if segment_counts.get("High-potential User", 0) > 50:
        return "High-potential User"
    if segment_counts.get("Silent User", 0) > 30:
        return "Silent User"
    return "Normal User"


def get_campaign_users(analysis_df, target_segment):
    """
    Build the campaign audience from segment and churn prediction results.
    """
    segment_match = analysis_df["User_Segment"] == target_segment
    churn_match = analysis_df["predicted_churn_risk"] == 1
    high_churn = analysis_df["churn_probability"] >= 0.5

    return analysis_df[segment_match | churn_match | high_churn].copy()


def estimate_campaign_metrics(campaign_users_df):
    """
    Estimate campaign impact using simple, readable business formulas.
    """
    user_count = len(campaign_users_df)

    if user_count == 0:
        return {
            "target_users": 0,
            "estimated_recovery_users": 0,
            "estimated_revenue_recovery": 0.0,
            "estimated_campaign_cost": 0.0,
            "estimated_roi": 0.0,
            "recovery_rate": 0.20,
        }

    recovery_rate = 0.20
    recovered_users = max(1, int(user_count * recovery_rate))

    if "Average_Order_Value" in campaign_users_df.columns:
        avg_order_value = float(campaign_users_df["Average_Order_Value"].mean())
    else:
        safe_frequency = campaign_users_df["Purchase_Frequency"].replace(0, 1)
        avg_order_value = float(
            (campaign_users_df["Total_Spending"] / safe_frequency).mean()
        )

    avg_spending = float(campaign_users_df["Total_Spending"].mean())
    revenue_capture_rate = 0.35

    revenue_recovery = (
        recovered_users
        * avg_order_value
        * revenue_capture_rate
)

    cost_per_user = 5.0
    campaign_cost = user_count * cost_per_user
    estimated_roi = (
        ((revenue_recovery - campaign_cost) / campaign_cost) * 100
        if campaign_cost > 0
        else 0.0
    )

    return {
        "target_users": user_count,
        "estimated_recovery_users": recovered_users,
        "estimated_revenue_recovery": revenue_recovery,
        "estimated_campaign_cost": campaign_cost,
        "estimated_roi": estimated_roi,
        "recovery_rate": recovery_rate,
    }


def get_execution_recommendations(target_segment):
    """Return recommended execution channels for the target segment."""
    return EXECUTION_RECOMMENDATIONS.get(
        target_segment,
        EXECUTION_RECOMMENDATIONS["default"],
    )


def build_campaign_context(
    segment_counts,
    analysis_df,
    avg_churn_probability,
    target_segment,
    metrics,
    execution_recommendations,
    ai_summary=None,
    ai_insights=None,
    ai_strategies=None,
):
    """Combine existing analytics into one prompt context block."""
    predicted_high_risk = int(analysis_df["predicted_churn_risk"].sum())
    segment_summary = segment_counts.to_string()
    insights_text = "\n".join(f"- {item}" for item in (ai_insights or []))
    strategies_text = "\n".join(f"- {item}" for item in (ai_strategies or []))
    execution_text = "\n".join(f"- {item}" for item in execution_recommendations)

    return f"""
Business Context:
- Target Segment: {target_segment}
- Total Users in Campaign Audience: {metrics['target_users']}
- Predicted High-risk Users: {predicted_high_risk}
- Average Churn Probability: {avg_churn_probability:.1%}
- Estimated Recovery Users: {metrics['estimated_recovery_users']}
- Estimated Revenue Recovery: ${metrics['estimated_revenue_recovery']:,.0f}
- Estimated Campaign Cost: ${metrics['estimated_campaign_cost']:,.0f}
- Estimated ROI: {metrics['estimated_roi']:.1f}%

Segment Distribution:
{segment_summary}

Previous AI Business Summary:
{ai_summary or "Not generated yet."}

Rule-based Risk Insights:
{insights_text or "- No insights generated yet."}

Existing Strategy Ideas:
{strategies_text or "- No strategies generated yet."}

Suggested Execution Channels:
{execution_text}
"""


def build_campaign_prompt(context):
    """Build the DeepSeek prompt for a structured retention campaign plan."""
    return f"""
You are an AI-powered e-commerce growth operations manager.

Based on the analytics context below, create a practical retention campaign plan.

Return the plan using EXACTLY these section headings:

Campaign Name:
Target Segment:
Recommended Action:
Suggested Offer:
Estimated Recovery Users:
Estimated ROI:
Campaign Priority:
Execution Timeline:
KPI Targets:

Requirements:
- Keep recommendations realistic and actionable
- Align with the provided segment and churn data
- Use professional business language
- Do not invent data that contradicts the context
- Execution timeline should be a simple 1-2 week plan

Analytics Context:
{context}
"""


def generate_retention_campaign(api_key, prompt):
    """Call DeepSeek to generate the retention campaign plan."""
    return chat_completion(
        api_key=api_key,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior e-commerce retention campaign strategist."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )


def format_campaign_plan_download(
    campaign_plan,
    target_segment,
    metrics,
    execution_recommendations,
):
    """Format the campaign plan for TXT download."""
    execution_text = "\n".join(f"- {item}" for item in execution_recommendations)

    return f"""AI RETENTION CAMPAIGN PLAN
==========================

Target Segment: {target_segment}
Campaign Audience Size: {metrics['target_users']}
Estimated Recovery Users: {metrics['estimated_recovery_users']}
Estimated Revenue Recovery: ${metrics['estimated_revenue_recovery']:,.0f}
Estimated Campaign Cost: ${metrics['estimated_campaign_cost']:,.0f}
Estimated ROI: {metrics['estimated_roi']:.1f}%

Recommended Execution Channels:
{execution_text}

AI GENERATED CAMPAIGN PLAN
==========================

{campaign_plan}
"""
