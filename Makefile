format:
	uv run ruff format . & \
	uv run isort .

run:
	uv run python -m streamlit run ./app/main.py