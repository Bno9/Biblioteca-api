<<<<<<< HEAD
FROM python:3.12-slim
    
WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000

=======
FROM python:3.12-slim
    
WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000

>>>>>>> 05818269784ef8305b45e650a9926ae345dd5818
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]