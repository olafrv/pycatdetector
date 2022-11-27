FROM ubuntu:22.04 as base
RUN apt update -y \
    && apt install -y python3 \
    && apt install -y python3.10-venv\
    && apt install -y --no-install-recommends build-essential gcc \
    && apt install -y ffmpeg \
    && apt clean

FROM base 
ENV PYTHONUNBUFFERED 1
WORKDIR /opt/pycatdetector
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /opt/pycatdetector
RUN pip install -Ur requirements.txt \
    && pip install --upgrade pip
RUN mkdir logs
COPY pycatdetector /opt/pycatdetector/pycatdetector
COPY *.py /opt/pycatdetector/
COPY config.yaml .
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT [ "python3" , "main.py" ]
CMD [ "-c" ]