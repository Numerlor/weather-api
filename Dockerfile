FROM python:3.10-slim

WORKDIR /code

RUN pip install pdm

COPY pyproject.toml pdm.lock ./

RUN pdm install --prod

COPY ./app /code/app

CMD ["pdm", "run", "uvicorn", "app.__main__:app", "--host", "0.0.0.0", "--port", "80"]
