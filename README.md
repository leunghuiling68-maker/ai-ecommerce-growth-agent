# AI E-Commerce Growth Agent

An AI-powered e-commerce growth analytics platform that combines customer segmentation, churn prediction, LLM-generated business insights, and retention campaign generation into a unified dashboard experience.

---

## Overview

This project simulates an AI-native growth analysis workflow for e-commerce platforms.

The system enables product teams and growth operators to:

- Analyze customer behavioral segments
- Predict churn-risk users
- Generate AI-powered business insights
- Simulate A/B testing strategies
- Launch retention campaign recommendations
- Interact with an AI growth copilot

The dashboard is designed to mimic a lightweight internal growth operating system used in modern consumer internet companies.

---

## Core Features

### Customer Segmentation

Behavior-based user clustering including:

- High-value users
- High-value churn-risk users
- Silent users
- High-potential users
- Normal users

---

### Churn Prediction Engine

Built a rule-based churn prediction module to identify at-risk users based on:

- Purchase frequency
- Session activity
- Engagement signals
- Retention behavior

Outputs include:

- Predicted churn population
- Average churn probability
- Segment-level risk analysis

---

### AI Business Analysis

Integrated LLM-powered business insight generation using DeepSeek API.

Generated outputs include:

- Executive business summary
- Key risk analysis
- User preference insights
- Marketing strategy recommendations
- A/B testing simulation

---

### AI Action Center

Automatically generates retention campaign plans for high-risk segments, including:

- Campaign objectives
- User targeting strategy
- Recommended incentives
- Expected conversion uplift
- Operational execution suggestions

---

### AI Copilot

Interactive AI assistant for growth analysis tasks.

Supports:

- User behavior interpretation
- Segment analysis
- Growth recommendation generation
- Marketing strategy consultation

---

## Tech Stack

### Frontend

- Streamlit

### Data Processing

- Pandas
- NumPy

### AI Integration

- DeepSeek API
- Prompt Engineering

### Visualization

- Streamlit Charts

### Backend Logic

- Python

---

## Project Structure

```bash
.
├── app.py
├── churn_model.py
├── action_center.py
├── copilot.py
├── llm_client.py
├── ui_components.py
├── tools.py
├── requirements.txt
└── user_personalized_features.csv
