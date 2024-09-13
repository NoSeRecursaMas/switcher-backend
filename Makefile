# Variables
VENV = venv
ACTIVATE = . $(VENV)/bin/activate

# Targets
run:
	( \
	   $(ACTIVATE); \
	   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000; \
	)

test:
	( \
	   $(ACTIVATE); \
	   pytest; \
	)

install:
	( \
	   python3 -m venv $(VENV); \
	   $(ACTIVATE); \
	   pip install -r requirements.txt; \
	)

docker-up:
	( \
	   docker-compose up --build; \
	)

docker-down:
	( \
	   docker-compose down; \
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