FROM python:3.9-alpine
WORKDIR /usr/local/src/app/pft
COPY . .
RUN mkdir /logs
CMD ["python", "core/server.py"]