FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir monolithic
COPY requirements.txt /monolithic
RUN pip install -r /monolithic/requirements.txt
COPY . /monolithic
RUN mv monolithic/app.ini .
RUN mv monolithic/wsgi.py .


