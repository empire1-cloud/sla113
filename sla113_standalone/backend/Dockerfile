FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create emergentintegrations symlink (from local backup in app/)
RUN ln -sf /app/app/emergentintegrations_local_backup /app/emergentintegrations

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
