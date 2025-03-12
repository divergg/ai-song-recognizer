FROM python:3.12-slim


WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./src ./src
COPY ./common_utils ./common_utils
COPY ./__main__.py ./__main__.py

CMD ["python", "."]