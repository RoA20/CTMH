run:
	source venv/bin/activate && \
	flask run --host=0.0.0.0 --port=5000

ngrok:
	ngrok http 5000
