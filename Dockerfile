FROM ubuntu:24.04

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        tzdata \
        python3 python3.12-venv \
        python3-tk \
        ffmpeg fonts-dejavu jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# This is required to autolink the package to the repository in github
LABEL org.opencontainers.image.source=https://github.com/olafrv/pycatdetector
LABEL org.opencontainers.image.description="Python Cat Detector"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /opt/pycatdetector
COPY requirements.txt /opt/pycatdetector

ENV PYTHONUNBUFFERED=1
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN --mount=type=cache,target=/root/.cache/pip pip3 install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -Ur requirements.txt
# RUN pip3 cache purge  # not needed as we use a cache mount, kept for reference

# Copy the package files
COPY pycatdetector /opt/pycatdetector/pycatdetector
COPY main.py /opt/pycatdetector/

CMD [ "python3" , "main.py" ]
