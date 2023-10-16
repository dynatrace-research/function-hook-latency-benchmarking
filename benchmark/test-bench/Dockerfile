FROM locustio/locust:2.17.0

WORKDIR /opt/locust

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY locustfile.py ./

EXPOSE 8089
