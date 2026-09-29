@echo off
title Automation Report OlshopERP
cd /d "c:\Report Automation"
echo ============================================================
echo  Menjalankan Automasi Laporan OlshopERP...
echo ============================================================
.\.venv\Scripts\python.exe update_clevel_report.py
echo.
echo Selesai! Halaman Notion Anda telah diperbarui.
pause
