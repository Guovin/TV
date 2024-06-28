FROM python:3.8-slim

WORKDIR /app

COPY . /app

# RUN pip install --trusted-host pypi.python.org Flask

EXPOSE 80

ENV NAME World

CMD ["python", "./main.py"]