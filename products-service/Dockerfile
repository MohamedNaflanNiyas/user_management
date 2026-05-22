FROM python:3.13.6-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Give the container permissions to execute our new startup script
RUN chmod +x run.sh

EXPOSE 5002

# Tell the container to execute run.sh when it boots up
CMD ["./run.sh"]