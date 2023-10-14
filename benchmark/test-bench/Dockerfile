FROM locustio/locust
WORKDIR /opt/locust

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY locustfile.py /mnt/locust/locustfile.py
COPY locustfile.py locustfile.py

# needed so locust can write csv files to mounted volume
User root
RUN mkdir cvs_exports
# RUN chmod 777 cvs_exports/
# User locust

EXPOSE 8089