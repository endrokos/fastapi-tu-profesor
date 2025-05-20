PORT=8000
APP=main:app

run:
	uvicorn $(APP) --reload --port $(PORT)

# Ejecutar el servidor sin recarga (producción local)
run-prod:
	uvicorn $(APP) --host 0.0.0.0 --port $(PORT)