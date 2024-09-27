# Variables
VENV = venv
ACTIVATE = . $(VENV)/bin/activate

# Targets
run-docker:
	( \
	   docker run -p 8000:80 -v .:/app backend; \
	)

build-docker:
	( \
	   docker build -t backend .; \
	)

run:
	( \
	   $(ACTIVATE); \
	   fastapi dev src/main.py --port 8000; \
	)

test:
	( \
	   $(ACTIVATE); \
	   pytest -rA; \
	)

install:
	( \
	   python3 -m venv $(VENV); \
	   $(ACTIVATE); \
	   pip install -r requirements.txt; \
	)

clean:
	( \
	   find . -type f -name "*.pyc" -delete; \
	   find . -type d -name "__pycache__" -delete; \
	)

open-docs:
	( \
	   $(ACTIVATE); \
	   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 & \
	   sleep 5; \
	   xdg-open http://localhost:8000/docs || open http://localhost:8000/docs || start http://localhost:8000/docs; \
	)
