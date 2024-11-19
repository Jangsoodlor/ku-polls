FROM python:3-alpine

ARG secret-key fake-secret-key
ARG hosts localhost,127.0.0.1,::1,testserver

WORKDIR /app/kupolls
COPY . .

ENV SECRET_KEY=${secret-key}
ENV ALLOWED_HOSTS=${hosts}
ENV TIME_ZONE=Asia/Bangkok
ENV DEBUG=True

# Install python dependencies in the docker container
RUN pip install -r requirements.txt

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]