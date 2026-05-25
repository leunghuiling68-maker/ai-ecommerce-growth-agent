# ==============================
# Tool 1: User Segmentation Tool
# ==============================

def classify_user(row):
    if row["Total_Spending"] > 4000 and row["Purchase_Frequency"] > 6:
        return "High-value User"

    elif row["Total_Spending"] > 3000 and row["Last_Login_Days_Ago"] > 20:
        return "High-value Churn-risk User"

    elif row["Pages_Viewed"] > 30 and row["Purchase_Frequency"] <= 2:
        return "High-potential User"

    elif row["Purchase_Frequency"] == 0:
        return "Silent User"

    else:
        return "Normal User"


# ==============================
# Tool 2: Segment Summary Tool
# ==============================

def summarize_segments(df):
    df["User_Segment"] = df.apply(classify_user, axis=1)
    return df["User_Segment"].value_counts()
# ==============================
# Tool 3: User Preference Analysis Tool
# ==============================
def analyze_user_preferences(df):
    """
    Analyze user interests, product category preferences,
    and newsletter subscription status.
    """

    preference_result = {
        "top_interests": df["Interests"].value_counts().head(5).to_dict(),

        "top_product_categories":
        df["Product_Category_Preference"]
        .value_counts()
        .head(5)
        .to_dict(),

        "newsletter_subscription_distribution":
        df["Newsletter_Subscription"]
        .value_counts()
        .to_dict()
    }

    return preference_result
# ==============================
# Tool 4: Risk Diagnosis Tool
# ==============================

def diagnose_risks(segment_counts):
    insights = []

    high_value = segment_counts.get("High-value User", 0)
    churn_risk = segment_counts.get("High-value Churn-risk User", 0)
    high_potential = segment_counts.get("High-potential User", 0)
    silent = segment_counts.get("Silent User", 0)

    if churn_risk > high_value:
        insights.append("Warning: High-value customer churn risk is increasing.")

    if high_potential > 50:
        insights.append("Opportunity: The platform has a strong high-potential user base for conversion optimization.")

    if silent < 100:
        insights.append("Customer activity level remains relatively healthy.")

    return insights


# ==============================
# Tool 4: KPI Tracking Tool
# ==============================

def generate_kpi_tracking_plan(segment_name):
    if segment_name == "High-value Churn-risk User":
        return [
            "Recall GMV",
            "7-day Repurchase Rate",
            "Coupon Redemption Rate",
            "Reactivation User Count"
        ]

    elif segment_name == "High-potential User":
        return [
            "GMV Uplift",
            "Conversion Rate",
            "Add-to-cart Rate",
            "Coupon Usage Rate"
        ]

    elif segment_name == "Silent User":
        return [
            "Reactivation Rate",
            "Return Visit Rate",
            "Campaign ROI"
        ]

    else:
        return [
            "GMV",
            "Retention Rate",
            "Repurchase Rate"
        ]
# ==============================
# Tool 5: A/B Test Simulation Tool
# ==============================

def simulate_ab_test(segment_name):
    """
    Simulate A/B testing results for marketing campaigns.
    """

    test_result = {
        "segment": segment_name,
        "control_conversion_rate": 0.12,
        "treatment_conversion_rate": 0.18,
        "uplift": "50%",
        "sample_size": 1000,
        "recommended_action": "Scale treatment strategy"
    }

    return test_result
# ==============================
# Tool 6: Strategy Recommendation Tool
# ==============================

def recommend_strategy(segment_name):

    if segment_name == "High-value Churn-risk User":

        return [
            "Send exclusive retention coupons",
            "Launch personalized reactivation campaigns",
            "Provide VIP customer benefits"
        ]


    elif segment_name == "High-potential User":

        return [
            "Push limited-time conversion discounts",
            "Recommend trending products",
            "Increase homepage exposure"
        ]


    elif segment_name == "Silent User":

        return [
            "Launch low-cost win-back campaigns",
            "Send reminder notifications",
            "Use lightweight engagement strategies"
        ]


    else:

        return [
            "Maintain regular operational campaigns"
        ]
   # ==============================
# Tool 7: Report Generator Tool
# ==============================

def generate_operation_report(target_segment, insights, strategies, tracking_metrics,preferences=None,ab_test_result=None):
    """
    Generate a structured operation report based on agent diagnosis results.
    """

    report = []

    report.append("========== AI Growth Operation Report ==========")
    report.append("")
    report.append(f"Priority Target Segment: {target_segment}")
    report.append("")

    report.append("1. Key Operational Insights")
    for insight in insights:
        report.append(f"- {insight}")

    report.append("")
    report.append("2. Recommended Strategies")
    for strategy in strategies:
        report.append(f"- {strategy}")

    report.append("")
    report.append("3. KPI Tracking Plan")
    for metric in tracking_metrics:
        report.append(f"- {metric}")
    report.append("")

    if preferences:
        report.append("4. User Preference Analysis")

        report.append("- Top Interests:")
        for interest, count in preferences.get("top_interests", {}).items():
            report.append(f"  - {interest}: {count}")

        report.append("- Top Product Categories:")
        for category, count in preferences.get("top_product_categories", {}).items():
            report.append(f"  - {category}: {count}")

        report.append("- Newsletter Subscription Distribution:")
        for status, count in preferences.get("newsletter_subscription_distribution", {}).items():
            report.append(f"  - {status}: {count}")
    report.append("")
    if ab_test_result:
        report.append("")
        report.append("5. A/B Test Simulation")

        report.append(
            f"- Control Conversion Rate: "
            f"{ab_test_result['control_conversion_rate']}"
        )

        report.append(
            f"- Treatment Conversion Rate: "
            f"{ab_test_result['treatment_conversion_rate']}"
        )

        report.append(
            f"- Conversion Uplift: "
            f"{ab_test_result['uplift']}"
        )

        report.append(
            f"- Sample Size: "
            f"{ab_test_result['sample_size']}"
        )

        report.append(
            f"- Recommended Action: "
            f"{ab_test_result['recommended_action']}"
        )
    report.append("6. Human Review Required")
    report.append("- Operators should review and confirm the recommended strategies before execution.")
    report.append("- High-risk marketing actions should not be executed automatically.")

    return "\n".join(report)     
# ==============================
# Tool 8: Prompt Builder Tool
# ==============================

def build_llm_prompt(report):

    prompt = f"""
You are a senior AI-powered e-commerce growth strategist.

Your task is to analyze the following operation report and provide:

1. Executive Summary
2. Key Business Risks
3. Recommended Growth Strategies
4. KPI Optimization Suggestions
5. Long-term Operational Recommendations

Requirements:
- Use professional business language
- Keep recommendations realistic and actionable
- Avoid hallucinated business claims
- Focus on user growth and retention

Operation Report:
{report}
"""

    return prompt