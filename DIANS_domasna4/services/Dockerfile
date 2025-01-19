FROM python:3.9-slim

WORKDIR /app

COPY services /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ENV FLASK_APP=indicator_microservice.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]