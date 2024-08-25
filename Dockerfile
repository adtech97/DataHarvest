FROM python:3.10-slim

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m venv /ETL
ENV PATH="/ETL/bin:$PATH"
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64

WORKDIR /etl_app

COPY requirements.txt .

RUN apt-get update && apt-get install -y postgresql-server-dev-all procps default-jdk
RUN /ETL/bin/pip install --no-cache-dir -r requirements.txt

COPY . /etl_app

# CMD ["sh", "-c", "/ETL/bin/python scripts.py && /ETL/bin/spark-submit --master local[*] --jars ./Driver/postgresql-42.7.1.jar ./ingest.py && /ETL/bin/spark-submit --master local[*] --jars ./Driver/postgresql-42.7.1.jar ./ingest_busRoute.py"]
CMD ["sh", "-c", "/ETL/bin/python scripts.py & /ETL/bin/spark-submit --master local[*] --jars ./Driver/postgresql-42.7.1.jar ./ingest.py & /ETL/bin/spark-submit --master local[*] --jars ./Driver/postgresql-42.7.1.jar ./ingest_busRoute.py"] 
