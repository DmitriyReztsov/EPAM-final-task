FROM python:3.8.10

RUN mkdir /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY final_task/ /app

WORKDIR /app

CMD ["python3", "server.py"]