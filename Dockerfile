FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir monolithic
COPY requirements.txt /monolithic/requirements.txt
RUN pip install -r /monolithic/requirements.txt
COPY . /monolithic

# ENV DOCKERIZE_VERSION v0.6.1
# RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \  
#     && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ENV FLASK_APP monolithic
ENV FLASK_ENV development

# RUN dockerize -wait tcp://db-server:5432 -timeout 20s

# RUN chmod +x /monolithic/env.sh  
# ENTRYPOINT /monolithic/env.sh 

# RUN flask db init
# RUN flask db migrate
# RUN flask db upgrade
CMD [ "flask", "run", "--host=0.0.0.0" ]
# EXPOSE 8001:5000


