"""
Reusable UI components and styles for the growth analytics dashboard.
"""

import html

import streamlit as st

from llm_client import DeepSeekAPIError

BADGE_STYLES = {
    "high_risk": {
        "label": "High Risk",
        "bg": "#fef2f2",
        "color": "#b91c1c",
        "border": "#fecaca",
    },
    "healthy": {
        "label": "Healthy",
        "bg": "#f0fdf4",
        "color": "#15803d",
        "border": "#bbf7d0",
    },
    "attention": {
        "label": "Attention Needed",
        "bg": "#fffbeb",
        "color": "#b45309",
        "border": "#fde68a",
    },
    "ai_generated": {
        "label": "AI Generated",
        "bg": "#eff6ff",
        "color": "#1d4ed8",
        "border": "#bfdbfe",
    },
}


def inject_dashboard_styles():
    """Inject global production-quality dashboard styles."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                -webkit-font-smoothing: antialiased;
            }

            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 100%;
            }
            section[data-testid="stSidebar"] {
                width: 280px !important;
                min-width: 280px !important;
            }
            h1 {
                font-size: clamp(1.45rem, 2vw, 1.85rem) !important;
                font-weight: 700 !important;
                letter-spacing: -0.025em;
                color: #0f172a !important;
                margin-bottom: 0.35rem !important;
            }

            [data-testid="stSidebar"] .block-container {
                padding-top: 1rem;
            }

            .dashboard-subtitle {
                color: #64748b;
                font-size: 0.92rem;
                line-height: 1.55;
                margin: 0 0 1.25rem 0;
            }

            .section-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-bottom: 0.85rem;
            }

            .panel-title {
                font-size: 1.02rem;
                font-weight: 600;
                color: #0f172a;
                margin: 0;
                letter-spacing: -0.015em;
            }

            .panel-subtitle {
                color: #64748b;
                font-size: 0.84rem;
                line-height: 1.5;
                margin: 0.15rem 0 0.85rem 0;
            }

            .badge-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                align-items: center;
            }

            .status-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.22rem 0.6rem;
                border-radius: 999px;
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 0.03em;
                white-space: nowrap;
                border: 1px solid transparent;
            }

            /* KPI grid */
            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(5, minmax(0, 1fr));
                gap: 0.85rem;
                width: 100%;
                margin-top: 0.15rem;
            }

            .kpi-card {
                background: #ffffff;
                border: 1px solid #e8edf3;
                border-radius: 14px;
                padding: 16px 14px;
                min-height: 112px;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04),
                            0 8px 24px rgba(15, 23, 42, 0.04);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-sizing: border-box;
                overflow: hidden;
                width: 100%;
            }

            .kpi-label {
                color: #64748b;
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                margin: 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .kpi-value {
                color: #0f172a;
                font-size: clamp(1.15rem, 1.45vw, 1.55rem);
                font-weight: 700;
                line-height: 1.1;
                margin: 10px 0 0 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            /* Panels & charts */
            [data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 14px !important;
                border-color: #e8edf3 !important;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04),
                            0 10px 28px rgba(15, 23, 42, 0.05);
                overflow: hidden;
            }

            [data-testid="stVerticalBlockBorderWrapper"] > div {
                padding: 0.9rem 1rem !important;
            }

            .chart-panel {
                padding: 0.35rem 0.15rem 0.65rem 0.15rem;
            }

            .empty-state {
                background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px dashed #cbd5e1;
                border-radius: 14px;
                padding: 1.75rem 1.25rem;
                color: #475569;
                text-align: center;
                font-size: 0.92rem;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
            }

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.25rem;
                overflow-x: auto;
                overflow-y: hidden;
                flex-wrap: nowrap;
                scrollbar-width: thin;
                padding-bottom: 0.15rem;
            }

            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 4px;
            }

            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 999px;
            }

            .stTabs [data-baseweb="tab"] {
                font-weight: 500;
                font-size: 0.82rem;
                padding: 0.48rem 0.8rem;
                white-space: nowrap;
                min-width: fit-content;
            }

            .stTabs [data-baseweb="tab-panel"] {
                padding-top: 0.85rem;
            }

            /* Loading */
            .skeleton-block {
                height: 76px;
                border-radius: 12px;
                margin: 0.35rem 0 0.85rem 0;
                background: linear-gradient(
                    90deg,
                    #f8fafc 0%,
                    #eef2f7 50%,
                    #f8fafc 100%
                );
                background-size: 200% 100%;
                animation: shimmer 1.5s ease-in-out infinite;
            }

            .loading-note {
                color: #64748b;
                font-size: 0.82rem;
                margin-top: -0.35rem;
            }

            @keyframes shimmer {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            /* Copilot */
            .copilot-shell {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(.copilot-chat-shell) {
                padding-bottom: 0.5rem !important;
            }

            .copilot-chat-shell [data-testid="stVerticalBlock"] {
                gap: 0.55rem;
            }

            div[data-testid="stChatMessage"] {
                border-radius: 14px;
                border: 1px solid #e8edf3;
                padding: 0.75rem 1rem;
                margin-bottom: 0.55rem;
                max-width: min(88%, 760px);
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
            }

            div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
                background: #f8fafc;
                margin-left: auto;
                border-color: #e2e8f0;
            }

            div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
                background: linear-gradient(180deg, #f8fbff 0%, #eff6ff 100%);
                border-left: 3px solid #2563eb;
                margin-right: auto;
            }

            div[data-testid="stChatMessage"] p,
            div[data-testid="stChatMessage"] li {
                font-size: 0.9rem;
                line-height: 1.6;
            }

            .copilot-input-shell {
                position: sticky;
                bottom: 0;
                z-index: 20;
                background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, #ffffff 24%);
                padding-top: 0.85rem;
                margin-top: 0.35rem;
                border-top: 1px solid #e8edf3;
            }

            /* Responsive */
            @media (max-width: 1200px) {
                .kpi-grid {
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                }
            }

            @media (max-width: 900px) {
                .kpi-grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }

                .kpi-card {
                    min-height: 100px;
                    padding: 14px 12px;
                }
            }

            @media (max-width: 640px) {
                .kpi-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title, subtitle=None, badges=None):
    """Render a section header with optional subtitle and badges."""
    badge_html = ""
    if badges:
        badge_parts = []
        for key in badges:
            style = BADGE_STYLES[key]
            label = html.escape(style["label"])
            badge_parts.append(
                f"""<span class="status-badge" style="
                    background:{style['bg']};
                    color:{style['color']};
                    border-color:{style['border']};
                ">{label}</span>"""
            )
        badge_html = f'<div class="badge-row">{"".join(badge_parts)}</div>'

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<p class="panel-subtitle">{html.escape(subtitle)}</p>'

    st.markdown(
        f"""
        <div class="section-header">
            <p class="panel-title">{html.escape(title)}</p>
            {badge_html}
        </div>
        {subtitle_html}
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label, value, accent_color, value_text=None):
    """Render a single KPI card."""
    display_value = value_text if value_text is not None else f"{value:,}"
    safe_label = html.escape(label)
    safe_value = html.escape(str(display_value))
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left: 4px solid {accent_color};">
            <p class="kpi-label" title="{safe_label}">{safe_label}</p>
            <p class="kpi-value" title="{safe_value}">{safe_value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(cards, columns=None):
    """
    Render KPI cards using native Streamlit metrics.
    """

    column_count = columns or len(cards)
    cols = st.columns(column_count)

    for idx, card in enumerate(cards):
        with cols[idx % column_count]:
            label = card.get("label", "")
            value = card.get("value_text", card.get("value", ""))
            st.metric(label=label, value=value)


def render_loading_skeleton(message="Generating AI response..."):
    """Show a loading skeleton while AI content is being generated."""
    st.markdown('<div class="skeleton-block"></div>', unsafe_allow_html=True)
    st.markdown(f'<p class="loading-note">{html.escape(message)}</p>', unsafe_allow_html=True)


def run_ai_generation(status_label, skeleton_message, generate_fn):
    """
    Run an AI task with loading UI, timeout-safe error handling,
    and a clear completion state.
    """
    with st.status(status_label, expanded=True) as status:
        render_loading_skeleton(skeleton_message)
        try:
            result = generate_fn()
            status.update(
                label=status_label.replace("...", "").strip() + " complete",
                state="complete",
            )
            return result
        except DeepSeekAPIError as exc:
            status.update(label="AI request failed", state="error")
            st.error(exc.user_message)
            return None


def get_health_badge(avg_churn_probability, predicted_high_risk, total_users):
    """Determine business health badge from churn metrics."""
    if total_users == 0:
        return "attention"

    risk_rate = predicted_high_risk / total_users

    if avg_churn_probability >= 0.35 or risk_rate >= 0.2:
        return "high_risk"
    if avg_churn_probability >= 0.15 or risk_rate >= 0.08:
        return "attention"
    return "healthy"
