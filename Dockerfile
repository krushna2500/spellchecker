FROM python:3.10

ARG APP_PATH=/app
ARG PYTHON_VERSION=3.10
ARG POETRY_VERSION=1.2.2
ARG POETRY_HOME="/opt/poetry"

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1\
    POETRY_HOME=${POETRY_HOME} 

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update \
    && apt-get install curl -y \
    && curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION}



WORKDIR $APP_PATH
# COPY pyproject.toml poetry.lock /$APP_PATH/
COPY . $APP_PATH

RUN poetry config virtualenvs.create false 

RUN echo "{$POETRY_VERSION}"

RUN poetry install --no-root

CMD [ "poetry", "run", "streamlit", "run", "main.py" ]
