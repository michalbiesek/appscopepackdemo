FROM cribl/scope:1.1.2 AS appscopeBuild

FROM python:3.10

WORKDIR /code

COPY --from=appscopeBuild /usr/local/bin/ldscope /usr/local/bin/ldscope

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/ .
