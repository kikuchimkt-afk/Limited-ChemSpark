@echo off
chcp 65001 >nul
echo ================================================
echo   ChemSpark 極 — ローカルサーバー起動
echo ================================================
echo.
echo   http://localhost:8000 でアクセスしてください
echo   停止するには Ctrl+C を押してください
echo.
echo ================================================
python serve.py
pause
