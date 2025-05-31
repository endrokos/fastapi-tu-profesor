PORT=8000
APP=main:app

run-api-resolutor:
	PYTHONPATH=api-resolutor uvicorn $(APP) --reload --port $(PORT)

run-register:
	PYTHONPATH=register uvicorn $(APP) --reload --port $(PORT)

# Ejecutar el servidor sin recarga (producción local)
run-prod:
	PYTHONPATH=$(PYTHONPATH) uvicorn $(APP) --host 0.0.0.0 --port $(PORT)