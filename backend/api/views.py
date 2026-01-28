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

        # --- HEALTH ENGINE (Kept) ---
        def calc_health(row):
            score = 100
            score -= abs(row['Pressure'] - 50) / 2
            score -= abs(row['Temperature'] - 40)
            return int(max(0, min(100, score)))

        df['Health'] = df.apply(calc_health, axis=1)

        # --- ACTION LOGIC (Kept) ---
        def get_action(row):
            if row['Health'] < 50: return "CRITICAL REPLACEMENT"
            if row['Health'] < 80: return "Urgent Repair"
            return "Routine Check"

        df['Action'] = df.apply(get_action, axis=1)

        # --- CLEAN SUMMARY ---
        # No financials, just operational data
        full_data = df.to_dict(orient='records')
        alerts = df[df['Health'] < 50].to_dict(orient='records')

        summary = {
            "total_count": int(df.shape[0]),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "ATTENTION" if len(alerts) > 0 else "OPERATIONAL",
            "averages": df[['Pressure', 'Temperature', 'Health']].mean().round(1).to_dict(),
            "distribution": df['Type'].value_counts().to_dict(),
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
        
        # Minimal Header
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, 750, "Equipment Health Report")
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.gray)
        p.drawString(50, 735, f"Date: {summary.get('timestamp')} | Status: {summary.get('status')}")
        
        p.setFillColor(colors.black)
        y = 700
        
        # Stats
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "System Overview")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(60, y, f"Total Units: {summary['total_count']}")
        y -= 15
        p.drawString(60, y, f"Avg Health: {summary['averages']['Health']}%")
        y -= 35
        
        # Table
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Equipment Status List")
        y -= 20
        p.setFont("Helvetica", 9)
        p.setFillColor(colors.gray)
        p.drawString(50, y, "UNIT NAME")
        p.drawString(200, y, "TYPE")
        p.drawString(300, y, "HEALTH")
        p.drawString(400, y, "ACTION")
        y -= 10
        p.line(50, y, 550, y)
        y -= 20
        p.setFillColor(colors.black)
        
        for item in summary['full_data']:
            if y < 50:
                p.showPage()
                y = 750
            p.drawString(50, y, item['Equipment Name'])
            p.drawString(200, y, item['Type'])
            
            # Health Color Logic for PDF
            health = item['Health']
            if health < 50: p.setFillColor(colors.red)
            elif health < 80: p.setFillColor(colors.orange)
            else: p.setFillColor(colors.green)
            
            p.drawString(300, y, f"{health}%")
            p.setFillColor(colors.black)
            p.drawString(400, y, item['Action'])
            y -= 20

        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')