"""
Churn prediction module using scikit-learn.

This module trains a simple model to predict user churn risk
based on customer behavior features.
"""

import pandas as pd
import plotly.express as px
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    "Total_Spending",
    "Purchase_Frequency",
    "Last_Login_Days_Ago",
    "Pages_Viewed",
]

CHURN_PROBABILITY_THRESHOLD = 0.5


def create_churn_label(df):
    """
    Create a simple rule-based churn label for model training.

    A user is labeled as churn-risk when:
    - Purchase_Frequency <= 1
    - Last_Login_Days_Ago > 30
    """
    return (
        (df["Purchase_Frequency"] <= 1)
        & (df["Last_Login_Days_Ago"] > 30)
    ).astype(int)


def _fallback_churn_probability(df):
    """
    Use a simple score when the dataset has only one churn class.
    """
    low_frequency = (df["Purchase_Frequency"] <= 1).astype(float)
    inactive_login = (df["Last_Login_Days_Ago"] > 30).astype(float)

    return ((low_frequency + inactive_login) / 2).clip(0, 1)


def add_churn_predictions(df):
    """
    Train a logistic regression model and add churn prediction columns.

    Returns a copy of the dataframe with:
    - churn_probability
    - predicted_churn_risk
    """
    model_df = df.copy()
    model_df["churn_label"] = create_churn_label(model_df)

    X = model_df[FEATURE_COLUMNS]
    y = model_df["churn_label"]

    if y.nunique() < 2:
        model_df["churn_probability"] = _fallback_churn_probability(model_df)
    else:
        X_train, _, y_train, _ = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
        model_df["churn_probability"] = model.predict_proba(X)[:, 1]

    model_df["predicted_churn_risk"] = (
        model_df["churn_probability"] >= CHURN_PROBABILITY_THRESHOLD
    ).astype(int)

    return model_df


def get_average_churn_probability(df):
    """Return the average churn probability across all users."""
    return float(df["churn_probability"].mean())


def build_churn_probability_chart(df):
    """Build a Plotly histogram of churn probabilities."""
    fig = px.histogram(
        df,
        x="churn_probability",
        nbins=30,
        title="Churn Probability Distribution",
        labels={"churn_probability": "Churn Probability"},
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_layout(
        bargap=0.05,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=20, r=20, t=50, b=20),
        height=360,
    )
    return fig


def build_spending_vs_churn_chart(df):
    """Build a Plotly scatter plot of spending vs churn probability."""
    fig = px.scatter(
        df,
        x="Total_Spending",
        y="churn_probability",
        color="predicted_churn_risk",
        title="Total Spending vs Churn Probability",
        labels={
            "Total_Spending": "Total Spending",
            "churn_probability": "Churn Probability",
            "predicted_churn_risk": "Predicted Churn Risk",
        },
        color_discrete_map={0: "#16a34a", 1: "#dc2626"},
        opacity=0.75,
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=20, r=20, t=50, b=20),
        height=360,
    )
    return fig
