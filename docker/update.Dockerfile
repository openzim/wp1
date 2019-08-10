FROM python:3.7

WORKDIR /usr/src

COPY lucky app
RUN pip3 install -r app/requirements.txt

ENTRYPOINT ["python", "app/update.py"]
