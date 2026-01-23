import pandas as pd
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import equipmentdata
from .serializers import equipmentdataserializer
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import datetime

class fileuploadview(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        
        try:
            df = pd.read_csv(file_obj)
        except:
            return Response({"error": "Invalid CSV"}, status=400)

        cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        if not all(c in df.columns for c in cols):
            return Response({"error": f"Missing columns: {cols}"}, status=400)

        # --- 1. HEALTH SCORING ENGINE ---
        def calc_health(row):
            score = 100
            # Penalize deviance from ideal (Pressure=50, Temp=40)
            score -= abs(row['Pressure'] - 50) / 2
            score -= abs(row['Temperature'] - 40)
            return int(max(0, min(100, score)))

        df['Health'] = df.apply(calc_health, axis=1)

        # --- 2. MAINTENANCE AI ENGINE ---
        def get_action(row):
            if row['Health'] > 85: return "Routine Check"
            if row['Pressure'] > 85: return "Release Valve Pressure"
            if row['Temperature'] > 80: return "Flush Coolant System"
            if row['Flowrate'] < 5: return "Clear Blockage"
            return "Full Diagnostic Required"

        df['Action'] = df.apply(get_action, axis=1)

        # --- 3. PREPARE SUMMARY DATA ---
        
        # Alerts: Only Critical Items (< 50% Health)
        alerts = df[df['Health'] < 50][['Equipment Name', 'Type', 'Action', 'Health']].to_dict(orient='records')
        
        # Risk Report: Top 10 lowest health items
        risk_report = df.sort_values('Health').head(10)[['Equipment Name', 'Type', 'Health', 'Action']].to_dict(orient='records')
        
        # Statistics
        numeric = df[['Flowrate', 'Pressure', 'Temperature', 'Health']]
        
        # Full Data for Live Sim (Limit to 500 rows for performance)
        full_data = df.head(500).to_dict(orient='records')

        summary = {
            "total_count": int(df.shape[0]),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_status": "CRITICAL" if len(alerts) > 0 else "OPTIMAL",
            "averages": numeric.mean().round(2).to_dict(),
            "distribution": df['Type'].value_counts().to_dict(),
            "alerts": alerts,
            "risk_report": risk_report,
            "full_data": full_data, 
        }

        equipmentdata.objects.create(file=file_obj, summary=summary)
        last_five = equipmentdata.objects.order_by('-uploaded_at')[:5]
        
        return Response({
            "current_analysis": summary,
            "history": equipmentdataserializer(last_five, many=True).data
        })

class pdfreportview(APIView):
    def get(self, request, *args, **kwargs):
        last_entry = equipmentdata.objects.last()
        if not last_entry: return Response({"error": "No data"}, 404)
        
        summary = last_entry.summary
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = 750  # Start Y position

        # --- HEADER ---
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, y, "Chemical Plant Detailed Analysis")
        y -= 25
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.gray)
        p.drawString(50, y, f"Generated: {summary.get('timestamp', 'N/A')} | Status: {summary.get('system_status', 'N/A')}")
        p.setFillColor(colors.black)
        y -= 40

        # --- EXECUTIVE SUMMARY ---
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "1. Executive Summary")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(70, y, f"Total Equipment Scanned: {summary['total_count']}")
        y -= 15
        p.drawString(70, y, f"System Health Status: {summary.get('system_status', 'Unknown')}")
        y -= 15
        p.drawString(70, y, f"Critical Alerts Found: {len(summary.get('alerts', []))}")
        y -= 30

        # --- SAFETY ALERTS (Red Section) ---
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "2. Critical Safety Alerts")
        y -= 20
        
        alerts = summary.get('alerts', [])
        if alerts:
            p.setFillColor(colors.red)
            p.setFont("Helvetica-Bold", 10)
            for item in alerts[:10]:  # Limit to 10 alerts to fit page
                if y < 100: # New Page if space runs out
                    p.showPage()
                    y = 750
                p.drawString(70, y, f"[URGENT] {item['Equipment Name']} ({item['Type']})")
                y -= 15
                p.setFont("Helvetica", 10)
                p.drawString(90, y, f"Issue: Low Health ({item['Health']}%) - Action: {item['Action']}")
                y -= 25
                p.setFont("Helvetica-Bold", 10)
            p.setFillColor(colors.black)
        else:
            p.setFont("Helvetica", 11)
            p.setFillColor(colors.green)
            p.drawString(70, y, "No critical safety violations detected.")
            p.setFillColor(colors.black)
        
        y -= 30

        # --- MAINTENANCE SCHEDULE ---
        if y < 200: 
            p.showPage()
            y = 750

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "3. Recommended Maintenance Actions")
        y -= 25
        
        p.setFont("Helvetica", 10)
        risk_report = summary.get('risk_report', [])
        
        # Table Header simulation
        p.drawString(70, y, "EQUIPMENT NAME")
        p.drawString(250, y, "HEALTH")
        p.drawString(350, y, "REQUIRED ACTION")
        y -= 5
        p.line(70, y, 550, y)
        y -= 15

        for item in risk_report:
            if y < 50:
                p.showPage()
                y = 750
            p.drawString(70, y, item['Equipment Name'])
            
            # Health Color Logic
            health = item['Health']
            if health < 50: p.setFillColor(colors.red)
            elif health < 80: p.setFillColor(colors.orange)
            else: p.setFillColor(colors.green)
            
            p.drawString(250, y, f"{health}%")
            p.setFillColor(colors.black)
            
            p.drawString(350, y, item['Action'])
            y -= 20

        # --- STATISTICS ---
        y -= 30
        if y < 150:
            p.showPage()
            y = 750
            
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "4. Operational Statistics")
        y -= 20
        p.setFont("Helvetica", 11)
        
        avgs = summary.get('averages', {})
        p.drawString(70, y, f"Avg Pressure: {avgs.get('Pressure', 0)} psi")
        y -= 15
        p.drawString(70, y, f"Avg Temperature: {avgs.get('Temperature', 0)} C")
        y -= 15
        p.drawString(70, y, f"Avg Flowrate: {avgs.get('Flowrate', 0)} L/m")
        y -= 15
        p.drawString(70, y, f"Avg System Health: {avgs.get('Health', 0)}%")

        p.showPage()
        p.save()
        
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')