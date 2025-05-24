# Dockerfile for ARM (aarch64) JMeter image
FROM arm64v8/openjdk:11-jre-slim

ENV JMETER_VERSION=5.4.1
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=${JMETER_HOME}/bin:$PATH

RUN apt-get update && \
    apt-get install -y wget unzip && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz && \
    tar -xzf apache-jmeter-${JMETER_VERSION}.tgz -C /opt/ && \
    rm apache-jmeter-${JMETER_VERSION}.tgz

# **여기서 JMX 테스트 플랜 복사**
COPY fastapi_test_plan.jmx /jmeter/fastapi_test_plan.jmx

WORKDIR ${JMETER_HOME}

CMD ["jmeter", "-n"]
