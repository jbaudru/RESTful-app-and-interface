# syntax=docker/dockerfile:1
FROM python:3.8

ENV LISTEN_PORT=5000
EXPOSE 5000:5000

RUN apt-get update
RUN pip install --pre flask flask-restful numpy pandas requests darts
WORKDIR /usr/src/app
COPY . .

CMD [ "python3", "-m" , "flask", "--app=demoAppPrediction", "--debug", "run", "--host=0.0.0.0"]
#CMD python demoAppPrediction.py 
