FROM python:3.12.7-bookworm

WORKDIR /app

RUN groupadd -r web && useradd -r -g web web

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY requirements_dev.txt .

RUN pip install -r requirements_dev.txt

COPY uwsgi.ini uwsgi.ini

COPY . .

EXPOSE 8003

ENTRYPOINT ["uwsgi", "--strict", "--ini", "uwsgi.ini"]
