@echo off
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxx
echo ✅ API Key Set!
echo Starting AI Shopping Assistant Server...
python -m uvicorn backend.main:app --reload
pause
