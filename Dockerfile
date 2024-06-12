FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY . /code
COPY ./.env /code/.env

# Install dependencies in a single layer
RUN apt-get update -y && \
    apt-get install -y libgdal-dev gdal-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"
ENV GDAL_CONFIG="/usr/bin/gdal-config"


RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8081
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.port", "8081"]
#  & /code/scripts/model_data-run.sh

