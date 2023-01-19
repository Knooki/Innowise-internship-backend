FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /code

COPY Pipfile Pipfile.lock ./

RUN python -m pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --dev --system --deploy

COPY . .
EXPOSE 8000

COPY . .

COPY . .

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh
