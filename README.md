# ⚗️ ChemViz Pro - Industrial Equipment Analytics

**ChemViz Pro** is a hybrid industrial analytics platform designed to monitor chemical plant equipment. It utilizes a unified **Django Backend** to serve consistent analytics to two distinct interfaces: a **React.js Web Dashboard** for remote monitoring and a **PyQt5 Desktop Controller** for on-site operators.

---

## 🚀 Key Features

### 1. Hybrid Architecture
- **Single Source of Truth:** A robust Django REST API processes data once and serves it to both Web and Desktop clients simultaneously.
- **Cross-Platform:** Seamlessly switch between the browser-based dashboard and the native desktop application.

### 2. 🧠 Smart Health Engine
- **Algorithmic Scoring:** A custom logic engine calculates a **Health Score (0-100%)** for every unit based on real-time sensor deviations (Pressure, Temperature, Flowrate).
- **Maintenance AI:** Automatically categorizes equipment status and recommends specific actions (e.g., *"Urgent Repair"* vs. *"Routine Check"*).

### 3. 💻 Modern Web Dashboard
- **Equipment Explorer:** A responsive, searchable table to filter through thousands of equipment units.
- **Visual Analytics:** Interactive charts visualize equipment distribution and type composition.
- **Critical Alerts:** Automatic flagging of "Red Status" units (Health < 50%).

### 4. 🖥️ Native Desktop Controller
- **Professional UI:** A clean, "Modern Light" interface designed for control rooms, featuring native progress bars and status indicators.
- **Health Monitor:** A dedicated grid view to track the live health status of all active assets.
- **Synchronized Data:** Instantly reflects data uploads made via the web interface.

### 5. 📄 Automated Reporting
- **PDF Export:** Generates professional maintenance reports with timestamped summaries.
- **Action Schedules:** Automatically compiles a list of "Critical Actions" for maintenance teams.

---

## 🛠️ Tech Stack

### **Backend (The Core)**
- **Framework:** Django 5.0 + Django REST Framework
- **Data Processing:** Pandas, NumPy
- **Reporting:** ReportLab (PDF Generation)
- **Database:** SQLite (Dev)

### **Web Frontend (Remote View)**
- **Framework:** React.js
- **Styling:** CSS3 (Glassmorphism & Modern UI)
- **Charting:** Chart.js
- **Networking:** Axios

### **Desktop Frontend (Operator View)**
- **Framework:** PyQt5 (Python Bindings for Qt)
- **Plotting:** Matplotlib Integration
- **Theme:** Custom QSS (Modern Light Enterprise Theme)

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm

### 1. Backend Setup
The backend must be running for the system to function.
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/chemical-equipment-visualizer.git](https://github.com/YOUR_USERNAME/chemical-equipment-visualizer.git)
cd chemical-equipment-visualizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run Migrations & Start Server
cd backend
python manage.py migrate
python manage.py runserver
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

📖 Usage Guide
Step 1: Data Ingestion
Launch either the Web or Desktop app.

Click "Upload Dataset" and select your CSV file (Schema: Equipment Name, Type, Flowrate, Pressure, Temperature).

The system will validate columns and process the health scores immediately.

Step 2: Monitor Health
Web: Use the "Equipment Explorer" tab to search for specific pumps or valves.

Desktop: Switch to the "Health Monitor" tab to see a native list with color-coded progress bars (Green/Orange/Red).

Step 3: Export Documentation
Click "Export PDF Report" on either platform.

The system will download a detailed PDF containing the executive summary and required maintenance actions.


### 📂 Project Structure
```bash
chemical-equipment-visualizer/
├── backend/                # Django Project & REST API
│   ├── api/                # Business Logic (Health Engine)
│   └── uploads/            # Temporary File Storage
├── web_frontend/           # React.js Dashboard
│   ├── src/                # Components & CSS
│   └── public/             # Assets
├── desktop_frontend/       # PyQt5 Application
│   └── main.py             # Desktop Entry Point
└── README.md               # Documentation
```
### Developed for FOSSEE Internship Submission 2026


