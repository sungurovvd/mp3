FROM python:3.9

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/
RUN apt-get update && apt-get install -y ffmpeg
COPY . /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]