#Dockerfile
FROM python:3.12-slim

#set working directory
WORKDIR /app

#copy and install dependancies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy app
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

