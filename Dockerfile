FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir monolithic
COPY requirements.txt /monolithic/requirements.txt
RUN pip install -r /monolithic/requirements.txt
COPY . /monolithic
RUN export FLASK_APP=monolithic
RUN export FLASK_ENV=development
EXPOSE 8001:5000
CMD []


