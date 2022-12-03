FROM ubuntu:22.04 as base
RUN apt update -y \
    && apt install -y python3 \
    && apt install -y python3.10-venv\
    && apt install -y --no-install-recommends build-essential gcc \
    && apt install -y ffmpeg \
    && apt clean

FROM base 

LABEL org.opencontainers.image.source=https://github.com/olafrv/pycatdetector
LABEL org.opencontainers.image.description="Python Cat Detector"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /opt/pycatdetector
COPY requirements.txt /opt/pycatdetector
COPY pycatdetector /opt/pycatdetector/pycatdetector
COPY main.py /opt/pycatdetector/

ENV PYTHONUNBUFFERED 1
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install -Ur requirements.txt \
    && pip install --upgrade pip
RUN python3 -c "from pycatdetector import NeuralNet; NeuralNet()";

ENTRYPOINT [ "python3" , "main.py" ]
CMD [ "-c" ]