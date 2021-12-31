FROM python:3.9-alpine
WORKDIR /usr/local/src/app/pft
COPY . .
RUN pip install -i --no-cache-dir -r requirements.txt
RUN mkdir /logs
CMD ["python", "core/server.py"]