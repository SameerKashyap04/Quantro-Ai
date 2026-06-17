# Quantro Personal AI

A private, AI-powered trading operating system designed for a single user.

## Overview
Quantro Personal AI provides decision support, technical indicator confluence, machine learning predictions, and disciplined execution routing. It monitors Indian stocks (NIFTY50), generates buy/sell signals, evaluates risk, and optionally connects to broker APIs.

**Objective**: Decision support and disciplined execution. **Not guaranteed profit.**

## Features
- **Market Data Engine**: Async data fetching and caching for Indian markets.
- **AI Prediction Engine**: Machine learning pipelines (RandomForest/GradientBoosting) mapped to market regimes.
- **Signal & Risk Engines**: Confluence of technicals and AI probabilities filtered by strict risk parameters (drawdown limits, sector concentration).
- **Execution & Portfolio**: Multi-mode execution (`paper`, `approval`, `auto`) and real-time PNL tracking.
- **Telegram Integration**: Push notifications for trade approvals and daily summaries.
- **Modern Dashboard**: React + Vite + Tailwind dashboard with premium dark-mode aesthetics.

## Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy (Async), asyncpg, APScheduler
- **Data/AI**: Pandas, NumPy, scikit-learn, yfinance, TA-Lib (or custom indicator implementations)
- **Frontend**: React 18, Vite, Zustand, Tailwind CSS, Shadcn UI
- **Infrastructure**: PostgreSQL, Redis, Docker, Docker Compose

## Quick Start (Docker)

1. **Clone & Configure**
   ```bash
   cp .env.example .env
   # Edit .env with your specific settings (Telegram tokens, Broker keys)
   ```

2. **Run Services**
   ```bash
   docker compose up -d --build
   ```

3. **Access**
   - Frontend Dashboard: `http://localhost:3001`
   - API Docs: `http://localhost:8000/docs`

## Disclaimer
This software is for personal educational and research purposes only. Auto-trading features (`TRADING_MODE=auto`) carry immense financial risk. **The authors and AI do not assume any responsibility for financial losses incurred.**
