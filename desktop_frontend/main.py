import sys
import requests
import webbrowser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QFrame, QTabWidget, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ChemicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemViz Pro | Desktop Controller")
        self.setGeometry(100, 100, 1280, 800)
        
        # --- MODERN LIGHT THEME (Matches Web App) ---
        self.setStyleSheet("""
            QMainWindow { background-color: #f1f5f9; } /* Slate-100 Background */
            QWidget { font-family: 'Segoe UI', 'Inter', sans-serif; color: #334155; }
            
            /* Sidebar */
            QFrame#Sidebar { 
                background-color: #ffffff; 
                border-right: 1px solid #e2e8f0; 
            }
            QLabel#Brand {
                font-size: 22px; font-weight: 800; color: #2563eb; /* Royal Blue */
                padding: 30px 25px;
            }
            
            /* Menu Buttons */
            QPushButton.MenuBtn {
                background-color: transparent;
                color: #64748b;
                text-align: left;
                padding: 14px 25px;
                border: none;
                font-size: 14px;
                font-weight: 600;
                margin: 4px 15px;
                border-radius: 8px;
            }
            QPushButton.MenuBtn:hover {
                background-color: #f8fafc;
                color: #2563eb;
            }
            QPushButton.MenuBtn:checked {
                background-color: #eff6ff; /* Light Blue Bg */
                color: #2563eb;
            }
            
            /* Action Button */
            QPushButton#ActionBtn {
                background-color: #2563eb; 
                color: white; 
                font-weight: 700;
                border-radius: 8px;
                padding: 12px;
                margin: 25px;
                border: none;
            }
            QPushButton#ActionBtn:hover { background-color: #1d4ed8; }
            
            /* Cards */
            QFrame.Card {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            
            /* Tables */
            QTableWidget {
                background-color: #ffffff;
                border: none;
                gridline-color: #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                color: #64748b;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: none;
                background-color: #f1f5f9;
                border-radius: 4px;
                text-align: center;
                color: transparent;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===========================
        # 1. SIDEBAR
        # ===========================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0,0,0,0)
        
        # Brand
        brand = QLabel("⚗️ ChemViz Pro")
        brand.setObjectName("Brand")
        side_layout.addWidget(brand)
        
        # Navigation
        side_layout.addWidget(QLabel("   MENU", styleSheet="color:#94a3b8; font-size:11px; font-weight:800; margin-top:10px; margin-bottom:5px;"))
        
        self.btn_dash = QPushButton("  Dashboard")
        self.btn_dash.setProperty("class", "MenuBtn")
        self.btn_dash.setCheckable(True)
        self.btn_dash.setChecked(True)
        self.btn_dash.clicked.connect(lambda: self.switch_tab(0))
        side_layout.addWidget(self.btn_dash)
        
        self.btn_health = QPushButton("  Health Monitor")
        self.btn_health.setProperty("class", "MenuBtn")
        self.btn_health.setCheckable(True)
        self.btn_health.clicked.connect(lambda: self.switch_tab(1))
        side_layout.addWidget(self.btn_health)
        
        side_layout.addStretch()
        
        # Status
        self.status_lbl = QLabel("●  System Ready")
        self.status_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight:600; margin-left: 25px;")
        side_layout.addWidget(self.status_lbl)

        # Upload Button
        self.btn_load = QPushButton("Upload Dataset")
        self.btn_load.setObjectName("ActionBtn")
        self.btn_load.clicked.connect(self.upload_file)
        side_layout.addWidget(self.btn_load)
        
        main_layout.addWidget(sidebar)

        # ===========================
        # 2. MAIN CONTENT
        # ===========================
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header Row
        header = QHBoxLayout()
        self.page_title = QLabel("Overview")
        self.page_title.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        header.addWidget(self.page_title)
        header.addStretch()
        
        self.btn_pdf = QPushButton("Export PDF Report")
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.setStyleSheet("""
            background-color: white; border: 1px solid #cbd5e1; 
            color: #475569; padding: 8px 16px; border-radius: 6px; font-weight: 600;
        """)
        self.btn_pdf.clicked.connect(self.download_pdf)
        header.addWidget(self.btn_pdf)
        
        content_layout.addLayout(header)
        
        # Hidden Tabs Container
        self.tabs = QTabWidget()
        self.tabs.tabBar().hide() # Hide default header
        self.tabs.setStyleSheet("border: none;")
        
        # -- Tab 1: Dashboard --
        self.tab_dash = QWidget()
        self.setup_dashboard()
        self.tabs.addTab(self.tab_dash, "")
        
        # -- Tab 2: Health Table --
        self.tab_health = QWidget()
        self.setup_health_table()
        self.tabs.addTab(self.tab_health, "")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content)

    def switch_tab(self, index):
        self.tabs.setCurrentIndex(index)
        self.btn_dash.setChecked(index == 0)
        self.btn_health.setChecked(index == 1)
        self.page_title.setText("Overview" if index == 0 else "System Health")

    def setup_dashboard(self):
        layout = QVBoxLayout(self.tab_dash)
        layout.setSpacing(25)
        
        # Stats Row
        stats_layout = QHBoxLayout()
        self.stat_labels = {}
        for title in ["TOTAL ASSETS", "AVG PRESSURE", "AVG TEMP"]:
            card = QFrame()
            card.setProperty("class", "Card")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(25, 25, 25, 25)
            
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;")
            lbl_v = QLabel("-")
            lbl_v.setStyleSheet("color: #0f172a; font-size: 32px; font-weight: 800; margin-top: 8px;")
            
            c_layout.addWidget(lbl_t)
            c_layout.addWidget(lbl_v)
            stats_layout.addWidget(card)
            self.stat_labels[title] = lbl_v
        layout.addLayout(stats_layout)
        
        # Charts Row
        charts_layout = QHBoxLayout()
        
        # Bar Chart
        bar_card = QFrame()
        bar_card.setProperty("class", "Card")
        b_layout = QVBoxLayout(bar_card)
        self.fig_bar = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_bar = FigureCanvas(self.fig_bar)
        b_layout.addWidget(QLabel("Equipment Distribution", styleSheet="font-weight:700; font-size:15px; border:none; margin-bottom:10px;"))
        b_layout.addWidget(self.canvas_bar)
        charts_layout.addWidget(bar_card, 2)
        
        # Pie Chart
        pie_card = QFrame()
        pie_card.setProperty("class", "Card")
        p_layout = QVBoxLayout(pie_card)
        self.fig_pie = Figure(figsize=(5, 3), dpi=100, facecolor='white')
        self.canvas_pie = FigureCanvas(self.fig_pie)
        p_layout.addWidget(QLabel("Type Breakdown", styleSheet="font-weight:700; font-size:15px; border:none; margin-bottom:10px;"))
        p_layout.addWidget(self.canvas_pie)
        charts_layout.addWidget(pie_card, 1)
        
        layout.addLayout(charts_layout)
        layout.addStretch()

    def setup_health_table(self):
        layout = QVBoxLayout(self.tab_health)
        
        card = QFrame()
        card.setProperty("class", "Card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(0,0,0,0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["EQUIPMENT NAME", "TYPE", "HEALTH SCORE", "RECOMMENDED ACTION"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #f8fafc;")
        
        c_layout.addWidget(self.table)
        layout.addWidget(card)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', "CSV (*.csv)")
        if not fname: return
        
        self.status_lbl.setText("●  Uploading...")
        try:
            files = {'file': open(fname, 'rb')}
            r = requests.post('http://127.0.0.1:8000/api/upload/', files=files)
            if r.status_code == 200:
                self.update_ui(r.json()['current_analysis'])
                self.status_lbl.setText("●  Data Active")
                self.status_lbl.setStyleSheet("color: #166534; font-size: 12px; font-weight:600; margin-left: 25px;")
            else:
                self.status_lbl.setText("●  Upload Error")
        except:
            self.status_lbl.setText("●  Connection Failed")
            self.status_lbl.setStyleSheet("color: #dc2626; font-size: 12px; font-weight:600; margin-left: 25px;")

    def update_ui(self, data):
        # 1. Update Stats
        self.stat_labels["TOTAL ASSETS"].setText(str(data['total_count']))
        self.stat_labels["AVG PRESSURE"].setText(f"{data['averages']['Pressure']}")
        self.stat_labels["AVG TEMP"].setText(f"{data['averages']['Temperature']}")
        
        # 2. Charts (Light Mode)
        dist = data['distribution']
        
        self.fig_bar.clear()
        ax1 = self.fig_bar.add_subplot(111)
        ax1.bar(dist.keys(), dist.values(), color='#3b82f6')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_color('#cbd5e1')
        ax1.spines['left'].set_color('#cbd5e1')
        self.canvas_bar.draw()
        
        self.fig_pie.clear()
        ax2 = self.fig_pie.add_subplot(111)
        ax2.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', 
                colors=['#3b82f6', '#10b981', '#f59e0b'])
        self.canvas_pie.draw()
        
        # 3. Table
        rows = data['full_data']
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            # Name
            name_item = QTableWidgetItem(row['Equipment Name'])
            name_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(i, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(row['Type'])
            type_item.setForeground(QColor("#64748b"))
            self.table.setItem(i, 1, type_item)
            
            # Health Bar
            health = int(row['Health'])
            pbar = QProgressBar()
            pbar.setValue(health)
            color = "#22c55e" if health > 80 else ("#eab308" if health > 50 else "#ef4444")
            pbar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}")
            self.table.setCellWidget(i, 2, pbar)
            
            # Action
            act_item = QTableWidgetItem(row['Action'])
            if health < 50:
                act_item.setForeground(QColor("#ef4444"))
                act_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            else:
                act_item.setForeground(QColor("#334155"))
            self.table.setItem(i, 3, act_item)

    def download_pdf(self):
        webbrowser.open('http://127.0.0.1:8000/api/report/')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChemicalApp()
    window.show()
    sys.exit(app.exec_())