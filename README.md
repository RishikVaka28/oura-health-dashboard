# 🧠 Seamless Sync Between Body and Cloud

An interactive health dashboard that syncs physiological and behavioral data from devices like the Oura Ring or exported CSVs into a PostgreSQL backend. This system visualizes trends in sleep, activity, and mood to help users monitor and improve their wellness journey.

## 📌 Overview

This project bridges the gap between body signals and cloud analytics. Using a combination of data ingestion, storage, and visual storytelling, it empowers users to interpret health data with clarity and control.

- Built using **Dash**, **Plotly**, **PostgreSQL**, and **Python**
- Visualizes live metrics: steps, sleep, mood, readiness
- Supports CSV log imports or real-time sync
- Mobile-responsive interface with animations

## 🛠️ Tech Stack

| Layer             | Technology              |
|------------------|--------------------------|
| Frontend         | Dash + Plotly            |
| Backend          | Python, Flask            |
| Database         | PostgreSQL               |
| Deployment (local)| Batch Scripts + WSL     |

## 🚀 How to Run Locally

1. **Clone the Repository**
   ```bash
   git clone https://github.com/RishikVaka28/seamless-sync-dashboard.git
   cd seamless-sync-dashboard
