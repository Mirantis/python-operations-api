FROM python:3.6-slim

# prepare directory
WORKDIR /code

# copy app
COPY . operations_api
RUN pip install ./operations_api

# run app
WORKDIR /code/operations_api
CMD ./scripts/entrypoint.sh
