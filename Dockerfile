FROM python:3.11

WORKDIR /app

# Установка зависимостей
RUN pip install --no-cache-dir "poetry==1.6.1"

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY . .