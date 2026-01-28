# ⚗️ ChemViz Pro - Advanced Chemical Equipment Analytics

**ChemViz Pro** is a hybrid industrial control system designed to monitor, analyze, and simulate chemical plant equipment data. It features a unified **Django Backend** that simultaneously powers a **React.js Web Dashboard** and a **PyQt5 Desktop Controller**.

---

## 🚀 Key Features

### 1. Hybrid Architecture
- **Single Source of Truth:** A robust Django REST API serves data to both Web and Desktop clients in real-time.
- **Cross-Platform:** Access analytics via a web browser (remote monitoring) or a native desktop app (control room station).

### 2. 🧠 Smart Health Engine
- **Predictive Scoring:** Automatically calculates a "Health Score" (0-100%) for every equipment unit based on sensor deviations.
- **Maintenance AI:** Algorithmic logic determines specific repairs (e.g., *"Flush Coolant"* vs. *"Release Valve"*) based on failure patterns.
- **Critical Alerts:** Auto-detection of safety violations (Pressure > 85 psi, Temp > 80°C).

### 3. 📡 Live Sensor Simulation (Desktop Exclusive)
- **Real-Time Feed:** Replays historical CSV datasets as a live sensor stream (1 reading/sec).
- **Industrial Interface:** Features digital LCD readouts, live telemetry graphs, and a scrolling system terminal.

### 4. 📊 Advanced Visualization
- **Correlation Matrix:** Heatmap visualization to detect relationships between Pressure, Temperature, and Flowrate.
- **Interactive Explorer:** Searchable and filterable equipment inventory with status badges.
- **PDF Reporting:** Generates professional maintenance reports with "Red Alert" sections for critical failures.

---

## 🛠️ Tech Stack

### **Backend (The Brain)**
- **Framework:** Django 5.0 + Django REST Framework
- **Data Processing:** Pandas, NumPy
- **Reporting:** ReportLab (PDF Generation)
- **Database:** SQLite (Dev) / PostgreSQL (Prod ready)

### **Web Frontend (The Dashboard)**
- **Framework:** React.js (Create React App)
- **Charting:** Chart.js, React-Chartjs-2
- **Styling:** Modern CSS3, Glassmorphism UI
- **Networking:** Axios

### **Desktop Frontend (The Controller)**
- **Framework:** PyQt5 (Python Bindings for Qt)
- **Plotting:** Matplotlib Integration
- **Theme:** Clean Enterprise Mode / Dark Industrial Mode

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm

### 1. Backend Setup
The backend must be running for either frontend to work.
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/chemical-equipment-visualizer.git](https://github.com/YOUR_USERNAME/chemical-equipment-visualizer.git)
cd chemical-equipment-visualizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install django djangorestframework pandas matplotlib pyqt5 requests reportlab django-cors-headers

# Run Migrations & Start Server
cd backend
python manage.py migrate
python manage.py runserver﻿# chemical-equipment-visualizer
```

### 2. Web Application Setup

```
# Open a new terminal
cd web_frontend

# Install Node modules
npm install

# Start the React Server
npm start

```
Access the dashboard at http://localhost:3000

### 3. Desktop Application Setup

```
# Open a new terminal (ensure venv is active)
cd desktop_frontend

# Run the Industrial Controller
python main.py

```

### 📖 Usage Guide

### Step 1: Ingest Data
**Launch the Web or Desktop app.**

**Upload a CSV file (Sample format: Equipment Name, Type, Flowrate, Pressure, Temperature).**

**The system will validate the schema and reject corrupt files.**

### Step 2: Analyze Risks
**Switch to the "Health Monitor" tab.**

**Identify equipment with Red Health Bars (< 50%).**

**Read the "Action Required" column to see the AI-recommended repair.**

### Step 3: Run Simulation (Desktop)
**Go to the "Real-Time Sensors" tab.**

**Click ▶ Start Live Feed.**

**Watch the LCD panels and Live Graph update in real-time as the system "replays" the dataset.**

### Step 4: Export Report
**Click "Download PDF Report".**

**The generated PDF includes a timestamped executive summary, a list of critical alerts, and a full maintenance schedule.**

### 📂 Project Structure
```bash
chemical-equipment-visualizer/
├── backend/                # Django Project
│   ├── api/                # REST API Logic (Views, Models, Serializers)
│   ├── core/               # Settings & URL Config
│   └── uploads/            # Temporary CSV storage
├── web_frontend/           # React.js Project
│   ├── src/                # Components, CSS, & Logic
│   └── public/             # Static Assets
├── desktop_frontend/       # PyQt5 Project
│   └── main.py             # Main Application Entry Point
├── .gitignore              # Git Exclusion Rules
└── README.md               # Documentation
```
### Developed for FOSSEE Internship Submission 2026

