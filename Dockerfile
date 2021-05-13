FROM python:3.6
WORKDIR /srv/api
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . /srv/api
CMD ["bash", "start.sh"]
