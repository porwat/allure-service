FROM python:3.13.0-alpine3.19
ENV ALLURE_VERSION=2.30.0
RUN apk add --no-cache &&\
    wget -O /etc/apk/keys/amazoncorretto.rsa.pub https://apk.corretto.aws/amazoncorretto.rsa.pub && \
    echo "https://apk.corretto.aws" >> /etc/apk/repositories && \
    apk update &&\
    apk add amazon-corretto-17 && \
    wget https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz && \
    mkdir /opt/allure && \
    tar -xf allure-${ALLURE_VERSION}.tgz -C /opt/allure && \
    rm allure-${ALLURE_VERSION}.tgz
ENV PATH="/opt/allure/allure-${ALLURE_VERSION}/bin:${PATH}"
COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]