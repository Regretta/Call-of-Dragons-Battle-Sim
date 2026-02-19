@echo off
py -m pip install -r requirements.txt
py -m pip install -r requirements-dev.txt
pyinstaller --noconfirm --onefile --windowed --name CoD_Sim_V1 ui_app.py --add-data "data;data" --add-data "spreadsheets;spreadsheets"
pause
