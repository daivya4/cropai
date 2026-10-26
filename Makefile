.PHONY: serve ui frontend test

# Run FastAPI backend
serve:
	PYTHONPATH=. ./venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Run React + Vite monochrome frontend
frontend:
	cd frontend && npm run dev -- --port 5173

# Run legacy Streamlit frontend
ui:
	./venv/bin/streamlit run app/streamlit_app.py --server.port=8501

# Run pytest unit and integration tests
test:
	PYTHONPATH=. ./venv/bin/pytest -v
