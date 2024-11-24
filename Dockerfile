FROM python:3-alpine

ARG secret-key
ARG hosts
ARG debug
ARG timezone

WORKDIR /app/kupolls
COPY . .

ENV SECRET_KEY=${secret-key}
ENV ALLOWED_HOSTS=${hosts}
ENV TIME_ZONE=${timezone}
ENV DEBUG=${debug}

# Install python dependencies in the docker container
RUN pip install -r requirements.txt

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]