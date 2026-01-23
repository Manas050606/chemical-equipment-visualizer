import sys
import requests
import webbrowser
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QFrame, QTabWidget, QLCDNumber, QTextEdit, 
                             QProgressBar, QListWidget, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ChemicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemViz Pro | Enterprise Edition")
        self.setGeometry(100, 100, 1280, 800)
        
        # --- Variables ---
        self.current_data = []
        self.sim_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

        # --- MODERN CLEAN THEME (CSS) ---
        self.setStyleSheet("""
            QMainWindow { background-color: #f3f4f6; }
            QWidget { font-family: 'Segoe UI', sans-serif; color: #1f2937; }
            
            /* Sidebar */
            QFrame#Sidebar { 
                background-color: #ffffff; 
                border-right: 1px solid #e5e7eb; 
            }
            QLabel#Logo {
                font-size: 20px; font-weight: bold; color: #111827;
                padding: 20px 10px;
            }
            QLabel#SectionLabel {
                font-size: 12px; font-weight: 600; color: #9ca3af;
                margin-left: 15px; margin-top: 20px;
            }
            
            /* Sidebar Buttons */
            QPushButton {
                background-color: transparent;
                color: #4b5563;
                text-align: left;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
                font-weight: 500;
                margin: 2px 10px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                color: #2563eb; /* Royal Blue */
            }
            QPushButton#PrimaryBtn {
                background-color: #2563eb; color: white;
                font-weight: bold; text-align: center;
            }
            QPushButton#PrimaryBtn:hover { background-color: #1d4ed8; }
            
            /* Cards */
            QFrame#Card {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
            }
            
            /* Tabs */
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: transparent;
                color: #6b7280;
                font-weight: 600;
                padding: 10px 0;
                margin-right: 25px;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 3px solid #2563eb;
            }
            
            /* LCD & Terminal */
            QLCDNumber { border: none; color: #111827; }
            QTextEdit { 
                background-color: #1f2937; color: #10b981; 
                border-radius: 8px; border: none; font-family: 'Consolas';
            }
            
            /* Health Bar */
            QProgressBar {
                border: none; background-color: #e5e7eb; border-radius: 4px;
                text-align: center; color: transparent;
            }
            QProgressBar::chunk { background-color: #10b981; border-radius: 4px; }
        """)

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===========================
        # 1. LEFT SIDEBAR
        # ===========================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        side_layout = QVBoxLayout(sidebar)
        
        # Logo
        logo = QLabel("🔹 ChemViz Pro")
        logo.setObjectName("Logo")
        side_layout.addWidget(logo)
        
        # Actions
        side_layout.addWidget(QLabel("DATA CONTROLS", objectName="SectionLabel"))
        
        self.btn_load = QPushButton("📂  Load Dataset")
        self.btn_load.clicked.connect(self.upload_file)
        side_layout.addWidget(self.btn_load)
        
        self.btn_report = QPushButton("📄  Export Report")
        self.btn_report.clicked.connect(self.download_pdf)
        side_layout.addWidget(self.btn_report)
        
        # Simulation Controls
        side_layout.addWidget(QLabel("SIMULATION", objectName="SectionLabel"))
        
        self.btn_start = QPushButton("▶  Start Live Feed")
        self.btn_start.clicked.connect(self.start_sim)
        side_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹  Stop Feed")
        self.btn_stop.clicked.connect(self.stop_sim)
        side_layout.addWidget(self.btn_stop)
        
        side_layout.addStretch()
        
        # Status Card
        status_card = QFrame()
        status_card.setStyleSheet("background: #eff6ff; border-radius: 8px; padding: 10px; margin: 10px;")
        sc_layout = QVBoxLayout(status_card)
        self.status_lbl = QLabel("● System Ready")
        self.status_lbl.setStyleSheet("color: #2563eb; font-weight: bold; border: none;")
        sc_layout.addWidget(self.status_lbl)
        side_layout.addWidget(status_card)
        
        main_layout.addWidget(sidebar)

        # ===========================
        # 2. MAIN CONTENT AREA
        # ===========================
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Dashboard Overview")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #111827;")
        header.addWidget(title)
        header.addStretch()
        content_layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        
        # --- TAB 1: OVERVIEW ---
        self.tab_overview = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.tab_overview, "Overview")
        
        # --- TAB 2: LIVE SENSOR ---
        self.tab_live = QWidget()
        self.setup_live_tab()
        self.tabs.addTab(self.tab_live, "Real-Time Sensors")
        
        # --- TAB 3: HEALTH GRID ---
        self.tab_health = QWidget()
        self.setup_health_tab()
        self.tabs.addTab(self.tab_health, "Equipment Health")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)

    # --- TAB SETUPS ---

    def setup_overview_tab(self):
        layout = QVBoxLayout(self.tab_overview)
        layout.setSpacing(20)
        
        # Stats Row
        stats_layout = QHBoxLayout()
        self.stat_cards = {}
        for title in ["Total Equipment", "Avg Pressure (psi)", "Avg Temp (°C)"]:
            card = QFrame(objectName="Card")
            c_layout = QVBoxLayout(card)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase;")
            
            lbl_val = QLabel("-")
            lbl_val.setStyleSheet("color: #111827; font-size: 32px; font-weight: 700;")
            
            c_layout.addWidget(lbl_title)
            c_layout.addWidget(lbl_val)
            stats_layout.addWidget(card)
            self.stat_cards[title] = lbl_val
            
        layout.addLayout(stats_layout)
        
        # Charts Row
        charts_layout = QHBoxLayout()
        
        # Bar Chart
        bar_frame = QFrame(objectName="Card")
        bar_layout = QVBoxLayout(bar_frame)
        self.fig_bar = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_bar = FigureCanvas(self.fig_bar)
        bar_layout.addWidget(QLabel("Equipment Distribution", styleSheet="font-weight:bold; font-size:16px; border:none;"))
        bar_layout.addWidget(self.canvas_bar)
        charts_layout.addWidget(bar_frame, 2)
        
        # Pie Chart
        pie_frame = QFrame(objectName="Card")
        pie_layout = QVBoxLayout(pie_frame)
        self.fig_pie = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_pie = FigureCanvas(self.fig_pie)
        pie_layout.addWidget(QLabel("Type Composition", styleSheet="font-weight:bold; font-size:16px; border:none;"))
        pie_layout.addWidget(self.canvas_pie)
        charts_layout.addWidget(pie_frame, 1)
        
        layout.addLayout(charts_layout, 1)

    def setup_live_tab(self):
        layout = QVBoxLayout(self.tab_live)
        
        # LCD Panel
        lcd_layout = QHBoxLayout()
        self.lcds = {}
        for label in ["PRESSURE", "TEMP", "FLOW", "HEALTH"]:
            card = QFrame(objectName="Card")
            c_layout = QVBoxLayout(card)
            c_layout.setAlignment(Qt.AlignCenter)
            
            l = QLabel(label)
            l.setStyleSheet("color:#6b7280; font-weight:bold; border:none;")
            
            lcd = QLCDNumber()
            lcd.setDigitCount(4)
            lcd.setSegmentStyle(QLCDNumber.Flat)
            lcd.setFixedHeight(50)
            lcd.setStyleSheet("border:none; color: #2563eb;")
            
            c_layout.addWidget(l)
            c_layout.addWidget(lcd)
            lcd_layout.addWidget(card)
            self.lcds[label] = lcd
        layout.addLayout(lcd_layout)
        
        # Monitor
        monitor_layout = QHBoxLayout()
        
        # Terminal
        term_frame = QFrame(objectName="Card")
        t_layout = QVBoxLayout(term_frame)
        t_layout.addWidget(QLabel("System Log", styleSheet="font-weight:bold; border:none;"))
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        t_layout.addWidget(self.terminal)
        monitor_layout.addWidget(term_frame, 1)
        
        # Live Graph
        graph_frame = QFrame(objectName="Card")
        g_layout = QVBoxLayout(graph_frame)
        g_layout.addWidget(QLabel("Live Telemetry", styleSheet="font-weight:bold; border:none;"))
        self.fig_live = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_live = FigureCanvas(self.fig_live)
        g_layout.addWidget(self.canvas_live)
        monitor_layout.addWidget(graph_frame, 1)
        
        layout.addLayout(monitor_layout, 1)

    def setup_health_tab(self):
        layout = QVBoxLayout(self.tab_health)
        
        list_frame = QFrame(objectName="Card")
        lf_layout = QVBoxLayout(list_frame)
        
        # Header
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("EQUIPMENT NAME", styleSheet="color:#6b7280; font-weight:bold; border:none;"))
        h_layout.addWidget(QLabel("HEALTH SCORE", styleSheet="color:#6b7280; font-weight:bold; border:none;"))
        h_layout.addWidget(QLabel("ACTION", styleSheet="color:#6b7280; font-weight:bold; border:none;"))
        lf_layout.addLayout(h_layout)
        
        self.health_list = QListWidget()
        self.health_list.setStyleSheet("border:none; background:transparent;")
        lf_layout.addWidget(self.health_list)
        
        layout.addWidget(list_frame)

    # --- LOGIC ---

    def log(self, msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        self.terminal.append(f"[{t}] > {msg}")

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open', '', "CSV (*.csv)")
        if not fname: return
        
        self.log(f"Loading {fname}...")
        try:
            files = {'file': open(fname, 'rb')}
            r = requests.post('http://127.0.0.1:8000/api/upload/', files=files)
            if r.status_code == 200:
                data = r.json()['current_analysis']
                self.current_data = data['full_data']
                self.update_ui(data)
                self.log("Dataset Loaded Successfully.")
                self.status_lbl.setText("● Data Loaded")
                self.status_lbl.setStyleSheet("color: #10b981; font-weight: bold; border: none;")
            else:
                self.log("Error: Upload Failed.")
        except:
            self.log("Connection Failed. Is Backend running?")

    def update_ui(self, data):
        # 1. Update Overview Stats
        self.stat_cards["Total Equipment"].setText(str(data['total_count']))
        self.stat_cards["Avg Pressure (psi)"].setText(str(round(data['averages']['Pressure'], 1)))
        self.stat_cards["Avg Temp (°C)"].setText(str(round(data['averages']['Temperature'], 1)))
        
        # 2. Charts (Matplotlib with Clean Style)
        dist = data['distribution']
        
        self.fig_bar.clear()
        ax1 = self.fig_bar.add_subplot(111)
        ax1.bar(dist.keys(), dist.values(), color='#3b82f6') # Blue bars
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        self.canvas_bar.draw()
        
        self.fig_pie.clear()
        ax2 = self.fig_pie.add_subplot(111)
        ax2.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', 
                colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444'])
        self.canvas_pie.draw()
        
        # 3. Health List
        self.health_list.clear()
        for row in data['full_data']:
            item_str = f"{row['Equipment Name']} ({row['Type']})   |   {row['Health']}%   |   {row['Action']}"
            self.health_list.addItem(item_str)

    def start_sim(self):
        if not self.current_data:
            self.log("No data loaded.")
            return
        self.sim_index = 0
        self.timer.start(1000)
        self.status_lbl.setText("● Live Feed Active")
        self.status_lbl.setStyleSheet("color: #ef4444; font-weight: bold; border: none;") # Red for 'Rec/Live'
        self.log("Starting Sensor Simulation...")

    def stop_sim(self):
        self.timer.stop()
        self.status_lbl.setText("● Feed Paused")
        self.status_lbl.setStyleSheet("color: #f59e0b; font-weight: bold; border: none;")
        self.log("Simulation Paused.")

    def update_simulation(self):
        if self.sim_index >= len(self.current_data):
            self.stop_sim()
            return
            
        row = self.current_data[self.sim_index]
        self.sim_index += 1
        
        self.lcds["PRESSURE"].display(row['Pressure'])
        self.lcds["TEMP"].display(row['Temperature'])
        self.lcds["FLOW"].display(row['Flowrate'])
        self.lcds["HEALTH"].display(row['Health'])
        
        # Update Live Chart
        self.fig_live.clear()
        ax = self.fig_live.add_subplot(111)
        # Simple vertical bars for sensors
        vals = [row['Pressure'], row['Temperature'], row['Flowrate']]
        ax.bar(['Pres', 'Temp', 'Flow'], vals, color=['#3b82f6', '#f59e0b', '#10b981'])
        ax.set_ylim(0, 150)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.canvas_live.draw()

    def download_pdf(self):
        webbrowser.open('http://127.0.0.1:8000/api/report/')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChemicalApp()
    window.show()
    sys.exit(app.exec_())