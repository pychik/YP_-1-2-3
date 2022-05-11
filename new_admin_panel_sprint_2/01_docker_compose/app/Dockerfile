FROM python:3.8

# WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir /staticfiles

COPY . .
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
