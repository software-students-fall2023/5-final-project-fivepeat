FROM python:3.12-slim

WORKDIR /usr/src/app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 5000

ENV NAME spotifyquiz

CMD ["pipenv", "run", "python", "./app.py"]