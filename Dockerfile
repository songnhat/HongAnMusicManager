FROM python:3.11-slim-buster

WORKDIR /python-docker

COPY requirements requirements

RUN python3 -m pip install wheel

RUN pip3 install -r requirements/base.txt

COPY . .

CMD [ "python3", "-m" , "flask", "--app", "HongAnMusicManager_app", "run", "--host=0.0.0.0", "--port=5000"]