FROM python:3.8-slim

WORKDIR /app

COPY check_images.py .

RUN pip install requests

CMD ["python", "check_images.py"]
