FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y net-tools

EXPOSE 8080

CMD ["python", "server.py", "0.0.0.0", "8080"]
