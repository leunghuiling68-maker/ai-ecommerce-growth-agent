import os

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
from llm_client import chat_completion

from ui_components import (
    get_health_badge,
    inject_dashboard_styles,
    render_kpi_grid,
    render_section_header,
    run_ai_generation,
)
from copilot import COPILOT_GENERATING_KEY, COPILOT_SESSION_KEY, render_copilot_tab
from action_center import (
    CAMPAIGN_SESSION_KEYS,
    build_campaign_context,
    build_campaign_prompt,
    estimate_campaign_metrics,
    format_campaign_plan_download,
    generate_retention_campaign,
    get_campaign_users,
    get_execution_recommendations,
    get_retention_target_segment,
)
from churn_model import (
    add_churn_predictions,
    build_churn_probability_chart,
    build_spending_vs_churn_chart,
    get_average_churn_probability,
)
from tools import (
    classify_user,
    summarize_segments,
    analyze_user_preferences,
    diagnose_risks,
    simulate_ab_test,
    generate_kpi_tracking_plan,
    recommend_strategy,
    generate_operation_report,
    build_llm_prompt,
)

st.set_page_config(page_title="AI Growth Agent", layout="wide")

inject_dashboard_styles()

# ==============================
# Sidebar: Upload & API Status
# ==============================

with st.sidebar:
    st.header("Control Panel")

    uploaded_file = st.file_uploader(
        "Customer CSV",
        type=["csv"],
        help="Upload a CSV file with customer behavior features.",
    )

    analyze_clicked = st.button("Analyze", use_container_width=True, type="primary")

    st.divider()

    st.subheader("API Status")

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if api_key:
        st.success("DeepSeek API key is configured.")
    else:
        st.warning(
            "DEEPSEEK_API_KEY is not set. "
            "Add it to your environment variables and restart the app."
        )

# ==============================
# Main Page Header
# ==============================

st.title("Growth Analytics Dashboard")
st.markdown(
    '<p class="dashboard-subtitle">Segment customers, predict churn, analyze insights, and launch AI-assisted campaigns.</p>',
    unsafe_allow_html=True,
)

# ==============================
# Analyze (business logic unchanged)
# ==============================

if uploaded_file is not None and analyze_clicked:

    for key in (
        "ai_summary",
        "ai_insights",
        "ai_target_segment",
        "ai_strategies",
        *CAMPAIGN_SESSION_KEYS,
        COPILOT_SESSION_KEY,
        COPILOT_GENERATING_KEY,
        "copilot_api_warning",
    ):
        st.session_state.pop(key, None)

    df = pd.read_csv(uploaded_file)

    df["User_Segment"] = df.apply(
        classify_user,
        axis=1
    )

    segment_counts = summarize_segments(df)

    df = add_churn_predictions(df)

    st.session_state["segment_counts"] = segment_counts
    st.session_state["analysis_df"] = df
    st.session_state["preview_df"] = df.head(20)
    st.session_state["avg_churn_probability"] = get_average_churn_probability(df)

# ==============================
# Results Dashboard
# ==============================

if (
    st.session_state.get("segment_counts") is not None
    and st.session_state.get("analysis_df") is not None
):

    segment_counts = st.session_state["segment_counts"]

    total_users = int(segment_counts.sum())
    high_value_users = int(segment_counts.get("High-value User", 0))
    churn_risk_users = int(segment_counts.get("High-value Churn-risk User", 0))
    high_potential_users = int(segment_counts.get("High-potential User", 0))
    avg_churn_probability = st.session_state.get("avg_churn_probability", 0.0)
    analysis_df = st.session_state["analysis_df"]
    predicted_high_risk = int(analysis_df["predicted_churn_risk"].sum())
    health_badge = get_health_badge(
        avg_churn_probability,
        predicted_high_risk,
        total_users,
    )

    with st.container(border=True):
        render_section_header(
            "Key Metrics",
            subtitle="Live customer health indicators from segmentation and churn models.",
            badges=[health_badge],
        )

        render_kpi_grid(
            [
                {"label": "Total Users", "value": total_users, "accent_color": "#64748b"},
                {"label": "High-value", "value": high_value_users, "accent_color": "#16a34a"},
                {"label": "At-risk", "value": churn_risk_users, "accent_color": "#dc2626"},
                {"label": "High-potential", "value": high_potential_users, "accent_color": "#2563eb"},
                {
                    "label": "Avg Churn",
                    "value": avg_churn_probability,
                    "accent_color": "#ea580c",
                    "value_text": f"{avg_churn_probability:.1%}",
                },
            ],
            columns=3,
        )

    tab_overview, tab_details, tab_churn, tab_ai, tab_action, tab_copilot = st.tabs(
        [
            "总览",
            "Segment Details",
            "Churn Prediction",
            "AI Business Analysis",
            "AI Action Center",
            "AI Copilot",
        ]
    )

    with tab_overview:
        chart_left, chart_right = st.columns(2, gap="medium")

    with chart_left:
        with st.container(border=True):
            render_section_header(
                "User Segment Distribution",
                subtitle="Distribution of customers across behavioral segments.",
            )
            st.bar_chart(segment_counts, height=320)

    with chart_right:
        with st.container(border=True):
            render_section_header(
                "Churn Risk Overview",
                subtitle="Comparison of predicted churn-risk and retained users.",
            )

            churn_overview = pd.DataFrame(
                {
                    "User Type": ["Predicted Churn Risk", "Others"],
                    "Count": [
                        predicted_high_risk,
                        total_users - predicted_high_risk,
                    ],
                }
            )

            st.bar_chart(
                churn_overview.set_index("User Type"),
                height=320,
            )
    with tab_details:
        detail_left, detail_right = st.columns([1, 2], gap="small")

        with detail_left:
            with st.container(border=True):
                render_section_header("Segment Counts")

                segment_df = segment_counts.reset_index()
                segment_df.columns = ["Segment", "Count"]
                st.dataframe(
                    segment_df,
                    use_container_width=True,
                    hide_index=True,
                )

        with detail_right:
            with st.container(border=True):
                render_section_header("Preview Data")

                st.dataframe(
                    st.session_state["preview_df"],
                    use_container_width=True,
                    hide_index=True,
                )

    with tab_churn:
        churn_badges = ["high_risk"] if health_badge == "high_risk" else [health_badge]

        with st.container(border=True):
            render_section_header(
                "ML Churn Prediction",
                subtitle="Logistic Regression predicts churn probability using spending, purchase frequency, login recency, and page views.",
                badges=churn_badges,
            )

            metric_left, metric_right = st.columns(2, gap="small")
            metric_left.metric("Predicted High-risk Users", predicted_high_risk)
            metric_right.metric(
                "Average Churn Probability",
                f"{avg_churn_probability:.1%}",
            )

        chart_left, chart_right = st.columns(2, gap="small")

        with chart_left:
            with st.container(border=True):
                render_section_header("Probability Distribution")
                st.markdown('<div class="chart-panel panel-body">', unsafe_allow_html=True)
                st.plotly_chart(
                    build_churn_probability_chart(analysis_df),
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

        with chart_right:
            with st.container(border=True):
                render_section_header("Spending vs Churn")
                st.markdown('<div class="chart-panel panel-body">', unsafe_allow_html=True)
                st.plotly_chart(
                    build_spending_vs_churn_chart(analysis_df),
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

        with st.container(border=True):
            render_section_header("Churn Prediction Results")
            churn_preview = analysis_df[
                [
                    "User_Segment",
                    "Total_Spending",
                    "Purchase_Frequency",
                    "Last_Login_Days_Ago",
                    "Pages_Viewed",
                    "churn_probability",
                    "predicted_churn_risk",
                ]
            ].head(20)
            st.dataframe(churn_preview, use_container_width=True, hide_index=True)

    with tab_ai:
        ai_badges = ["ai_generated"] if st.session_state.get("ai_summary") else ["attention"]

        with st.container(border=True):
            render_section_header(
                "AI Business Analysis",
                subtitle="Generate an AI-powered business summary, risk analysis, and marketing recommendations.",
                badges=ai_badges,
            )

            if st.button("Generate AI Insights", type="primary"):
                api_key = os.getenv("DEEPSEEK_API_KEY")

                if not api_key:
                    st.warning(
                        "DEEPSEEK_API_KEY is not set. "
                        "Add it to your environment variables and restart the app."
                    )
                else:
                    insights = diagnose_risks(segment_counts)

                    if segment_counts.get("High-value Churn-risk User", 0) > 100:
                        target_segment = "High-value Churn-risk User"
                    elif segment_counts.get("High-potential User", 0) > 50:
                        target_segment = "High-potential User"
                    elif segment_counts.get("Silent User", 0) > 30:
                        target_segment = "Silent User"
                    else:
                        target_segment = "Normal User"

                    strategies = recommend_strategy(target_segment)
                    tracking_metrics = generate_kpi_tracking_plan(target_segment)
                    preferences = analyze_user_preferences(analysis_df)
                    ab_test_result = simulate_ab_test(target_segment)

                    report = generate_operation_report(
                        target_segment,
                        insights,
                        strategies,
                        tracking_metrics,
                        preferences,
                        ab_test_result,
                    )

                    messages = [
                        {
                            "role": "system",
                            "content": (
                                "You are a senior AI-powered "
                                "e-commerce growth strategist."
                            ),
                        },
                        {
                            "role": "user",
                            "content": build_llm_prompt(report),
                        },
                    ]

                    ai_summary = run_ai_generation(
                        "Generating AI business insights...",
                        "Analyzing segments, risks, and growth opportunities...",
                        lambda: chat_completion(api_key=api_key, messages=messages),
                    )

                    if ai_summary:
                        st.session_state["ai_summary"] = ai_summary
                        st.session_state["ai_insights"] = insights
                        st.session_state["ai_target_segment"] = target_segment
                        st.session_state["ai_strategies"] = strategies
                        st.session_state["ai_preferences"] = preferences
                        st.session_state["ai_ab_test_result"] = ab_test_result
            if st.session_state.get("ai_summary"):
                render_section_header(
                    "Generated Insights",
                    badges=["ai_generated"],
                )
                with st.expander("Business Summary", expanded=True):
                    st.write(st.session_state["ai_summary"])
                with st.expander("User Preference Analysis", expanded=False):
                    st.write(st.session_state["ai_preferences"])

                with st.expander("A/B Test Simulation", expanded=False):
                    st.write(st.session_state["ai_ab_test_result"])
                with st.expander("Key Risks", expanded=True):
                    for insight in st.session_state["ai_insights"]:
                        st.write(f"- {insight}")

                with st.expander("Marketing Strategies", expanded=True):
                    st.write(f"**Target segment:** {st.session_state['ai_target_segment']}")
                    for strategy in st.session_state["ai_strategies"]:
                        st.write(f"- {strategy}")
                st.download_button(
                    label="Download AI Report",
                    data=st.session_state["ai_summary"],
                    file_name="ai_growth_report.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
    with tab_action:
        action_badges = (
            ["ai_generated"] if st.session_state.get("campaign_plan") else ["attention"]
        )

        with st.container(border=True):
            render_section_header(
                "AI Action Center",
                subtitle="Turn analytics into executable retention campaigns with AI-generated plans and downloadable outputs.",
                badges=action_badges,
            )

            if st.button("Generate Retention Campaign", type="primary"):
                api_key = os.getenv("DEEPSEEK_API_KEY")

                if not api_key:
                    st.warning(
                        "DEEPSEEK_API_KEY is not set. "
                        "Add it to your environment variables and restart the app."
                    )
                else:
                    target_segment = get_retention_target_segment(segment_counts)
                    campaign_users_df = get_campaign_users(analysis_df, target_segment)
                    metrics = estimate_campaign_metrics(campaign_users_df)
                    execution_recommendations = get_execution_recommendations(
                        target_segment
                    )

                    context = build_campaign_context(
                        segment_counts=segment_counts,
                        analysis_df=analysis_df,
                        avg_churn_probability=avg_churn_probability,
                        target_segment=target_segment,
                        metrics=metrics,
                        execution_recommendations=execution_recommendations,
                        ai_summary=st.session_state.get("ai_summary"),
                        ai_insights=st.session_state.get("ai_insights"),
                        ai_strategies=st.session_state.get("ai_strategies"),
                    )

                    prompt = build_campaign_prompt(context)

                    campaign_plan = run_ai_generation(
                        "Generating retention campaign plan...",
                        "Building campaign strategy and impact estimates...",
                        lambda: generate_retention_campaign(api_key, prompt),
                    )

                    if campaign_plan:
                        st.session_state["campaign_plan"] = campaign_plan
                        st.session_state["campaign_metrics"] = metrics
                        st.session_state["campaign_users_df"] = campaign_users_df
                        st.session_state["campaign_target_segment"] = target_segment
                        st.session_state["execution_recommendations"] = (
                            execution_recommendations
                        )

            if st.session_state.get("campaign_plan"):
                metrics = st.session_state["campaign_metrics"]
                target_segment = st.session_state["campaign_target_segment"]
                execution_recommendations = st.session_state[
                    "execution_recommendations"
                ]
                with st.container(border=True):
                    render_section_header(
                        "营销效果预估",
                        badges=["ai_generated"],
                    )

                with st.container(border=True):
                    render_section_header("Execution Recommendations")
                    st.write(f"**Target segment:** {target_segment}")
                    st.write(f"**Audience size:** {metrics['target_users']} users")
                    for item in execution_recommendations:
                        st.write(f"- {item}")

                with st.container(border=True):
                    render_section_header("Download Outputs")

                    campaign_txt = format_campaign_plan_download(
                        st.session_state["campaign_plan"],
                        target_segment,
                        metrics,
                        execution_recommendations,
                    )
                    campaign_csv = st.session_state["campaign_users_df"].to_csv(
                        index=False
                    )

                    st.download_button(
                        label="Download Campaign Plan (TXT)",
                        data=campaign_txt,
                        file_name="retention_campaign_plan.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
              
                    st.download_button(
                            label="Download Campaign User List (CSV)",
                            data=campaign_csv,
                            file_name="campaign_user_list.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                with st.container(border=True):
                    render_section_header("Campaign Audience Preview")
                    preview_columns = [
                        col
                        for col in [
                            "User_ID",
                            "User_Segment",
                            "Total_Spending",
                            "Purchase_Frequency",
                            "Last_Login_Days_Ago",
                            "churn_probability",
                            "predicted_churn_risk",
                        ]
                        if col in st.session_state["campaign_users_df"].columns
                    ]
                    st.dataframe(
                        st.session_state["campaign_users_df"][preview_columns].head(20),
                        use_container_width=True,
                        hide_index=True,
                    )

    with tab_copilot:
        render_copilot_tab(
            segment_counts=segment_counts,
            analysis_df=analysis_df,
            avg_churn_probability=avg_churn_probability,
            api_key=api_key,
        )

else:
    st.markdown(
        '<div class="empty-state">Upload a CSV in the sidebar and click <strong>Analyze</strong> to load the dashboard.</div>',
        unsafe_allow_html=True,
    )
