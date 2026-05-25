"""
AI Copilot module for context-aware growth strategy chat.

Answers executive questions using dashboard analytics context.
"""

from llm_client import chat_completion
from ui_components import render_section_header, run_ai_generation

COPILOT_SESSION_KEY = "copilot_messages"
COPILOT_GENERATING_KEY = "copilot_generating"

COPILOT_SYSTEM_PROMPT = """
You are an AI growth strategist copilot for an e-commerce platform.

Your job is to help business operators understand customer segments, churn risk,
KPI priorities, campaign ROI, and overall business health.

Guidelines:
- Answer clearly and concisely in executive-friendly language
- Ground answers in the analytics context provided below
- If data is missing, say what is unavailable and suggest next steps
- Recommend practical actions when relevant
- Do not invent numbers that are not supported by the context
"""

EXAMPLE_QUESTIONS = [
    "Which users are highest risk?",
    "Why is churn increasing?",
    "What KPI should we prioritize?",
    "Which campaign has best ROI?",
    "Summarize current business health.",
]


def build_copilot_context(
    segment_counts,
    analysis_df,
    avg_churn_probability,
    ai_summary=None,
    ai_insights=None,
    ai_strategies=None,
    ai_target_segment=None,
    campaign_plan=None,
    campaign_metrics=None,
    campaign_target_segment=None,
):
    """Build analytics context for the copilot system prompt."""
    total_users = int(segment_counts.sum())
    predicted_high_risk = int(analysis_df["predicted_churn_risk"].sum())
    high_risk_users = analysis_df.nlargest(5, "churn_probability")

    high_risk_lines = []
    for _, row in high_risk_users.iterrows():
        user_id = row.get("User_ID", "Unknown")
        high_risk_lines.append(
            f"- {user_id}: segment={row['User_Segment']}, "
            f"churn_probability={row['churn_probability']:.1%}, "
            f"spending={row['Total_Spending']:.0f}"
        )

    insights_text = "\n".join(f"- {item}" for item in (ai_insights or []))
    strategies_text = "\n".join(f"- {item}" for item in (ai_strategies or []))

    campaign_section = "No retention campaign generated yet."
    if campaign_plan and campaign_metrics:
        campaign_section = f"""
Target Segment: {campaign_target_segment}
Estimated ROI: {campaign_metrics['estimated_roi']:.1f}%
Estimated Revenue Recovery: ${campaign_metrics['estimated_revenue_recovery']:,.0f}
Estimated Campaign Cost: ${campaign_metrics['estimated_campaign_cost']:,.0f}
Estimated User Recovery: {campaign_metrics['estimated_recovery_users']}

Campaign Plan Summary:
{campaign_plan[:1200]}
"""

    return f"""
CURRENT ANALYTICS CONTEXT
=========================

Business Overview:
- Total Users: {total_users}
- Average Churn Probability: {avg_churn_probability:.1%}
- Predicted High-risk Users: {predicted_high_risk}

Segment Distribution:
{segment_counts.to_string()}

Top 5 Highest Churn-risk Users:
{chr(10).join(high_risk_lines)}

AI Business Analysis:
- Target Segment: {ai_target_segment or "Not generated yet"}
- Summary: {ai_summary or "Not generated yet"}

Risk Insights:
{insights_text or "- Not generated yet"}

Recommended Strategies:
{strategies_text or "- Not generated yet"}

Campaign Planning Output:
{campaign_section}
"""


def generate_copilot_response(api_key, system_context, chat_history, user_message):
    """Generate a copilot response using DeepSeek and chat history."""
    messages = [
        {"role": "system", "content": COPILOT_SYSTEM_PROMPT + system_context},
        *chat_history,
        {"role": "user", "content": user_message},
    ]
    return chat_completion(api_key=api_key, messages=messages)


def _process_user_message(user_message, api_key, system_context):
    """Append user message, call API, and append assistant reply."""
    import streamlit as st

    if COPILOT_SESSION_KEY not in st.session_state:
        st.session_state[COPILOT_SESSION_KEY] = []

    st.session_state[COPILOT_SESSION_KEY].append(
        {"role": "user", "content": user_message}
    )

    history = st.session_state[COPILOT_SESSION_KEY][:-1]

    def _generate():
        return generate_copilot_response(
            api_key=api_key,
            system_context=system_context,
            chat_history=history,
            user_message=user_message,
        )

    reply = run_ai_generation(
        "Generating AI copilot response...",
        "Reviewing analytics context and preparing answer...",
        _generate,
    )

    if reply is None:
        st.session_state[COPILOT_SESSION_KEY].append(
            {
                "role": "assistant",
                "content": (
                    "I couldn't complete that request. "
                    "Please check your connection or try again shortly."
                ),
            }
        )
        return False

    st.session_state[COPILOT_SESSION_KEY].append(
        {"role": "assistant", "content": reply}
    )
    return True


def render_copilot_tab(
    segment_counts,
    analysis_df,
    avg_churn_probability,
    api_key,
):
    """Render the AI Copilot chat tab."""
    import streamlit as st

    with st.container(border=True):
        copilot_badges = (
            ["ai_generated"] if st.session_state.get(COPILOT_SESSION_KEY) else []
        )
        render_section_header(
            "AI Copilot",
            subtitle="Ask questions about segments, churn, KPIs, campaigns, and overall business health.",
            badges=copilot_badges or None,
        )

        system_context = build_copilot_context(
            segment_counts=segment_counts,
            analysis_df=analysis_df,
            avg_churn_probability=avg_churn_probability,
            ai_summary=st.session_state.get("ai_summary"),
            ai_insights=st.session_state.get("ai_insights"),
            ai_strategies=st.session_state.get("ai_strategies"),
            ai_target_segment=st.session_state.get("ai_target_segment"),
            campaign_plan=st.session_state.get("campaign_plan"),
            campaign_metrics=st.session_state.get("campaign_metrics"),
            campaign_target_segment=st.session_state.get("campaign_target_segment"),
        )

        if COPILOT_SESSION_KEY not in st.session_state:
            st.session_state[COPILOT_SESSION_KEY] = []

        is_generating = st.session_state.get(COPILOT_GENERATING_KEY, False)
        chat_col, side_col = st.columns([3, 1], gap="small")

        with side_col:
            with st.container(border=True):
                render_section_header("Quick Questions")

                for index, question in enumerate(EXAMPLE_QUESTIONS):
                    if st.button(
                        question,
                        key=f"copilot_example_{index}",
                        use_container_width=True,
                        disabled=is_generating,
                    ):
                        if not api_key:
                            st.session_state["copilot_api_warning"] = True
                        else:
                            st.session_state[COPILOT_GENERATING_KEY] = True
                            _process_user_message(question, api_key, system_context)
                            st.session_state[COPILOT_GENERATING_KEY] = False
                        st.rerun()

                if st.button(
                    "Clear Chat",
                    use_container_width=True,
                    disabled=is_generating,
                ):
                    st.session_state[COPILOT_SESSION_KEY] = []
                    st.rerun()

        with chat_col:
            with st.container(border=True):
                st.markdown('<div class="copilot-chat-shell">', unsafe_allow_html=True)
                render_section_header(
                    "Strategy Chat",
                    badges=["ai_generated"]
                    if st.session_state.get(COPILOT_SESSION_KEY)
                    else None,
                )

                if st.session_state.get("copilot_api_warning"):
                    st.warning(
                        "DEEPSEEK_API_KEY is not set. "
                        "Add it to your environment variables and restart the app."
                    )
                    st.session_state["copilot_api_warning"] = False

                with st.container(height=430, border=False):
                    if not st.session_state[COPILOT_SESSION_KEY] and not is_generating:
                        st.info(
                            "Start a conversation with your AI growth strategist. "
                            "Try asking about churn risk, KPI priorities, or campaign ROI."
                        )

                    for message in st.session_state[COPILOT_SESSION_KEY]:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                st.markdown('<div class="copilot-input-shell">', unsafe_allow_html=True)
                user_input = st.chat_input(
                    "Ask about segments, churn, KPIs, campaigns, or business health...",
                    disabled=is_generating,
                )
                st.markdown("</div></div>", unsafe_allow_html=True)

                if user_input:
                    if not api_key:
                        st.session_state["copilot_api_warning"] = True
                        st.rerun()

                    st.session_state[COPILOT_GENERATING_KEY] = True
                    _process_user_message(user_input, api_key, system_context)
                    st.session_state[COPILOT_GENERATING_KEY] = False
                    st.rerun()
