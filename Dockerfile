FROM ubuntu:22.04
RUN apt update -y \
    && apt install -y tzdata \
    && apt install -y python3 \
    && apt install -y python3.10-venv\
    && apt install -y --no-install-recommends build-essential gcc \
    && apt install -y ffmpeg \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# This is required to autolink the package to the repository in github
LABEL org.opencontainers.image.source=https://github.com/olafrv/pycatdetector
LABEL org.opencontainers.image.description="Python Cat Detector"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /opt/pycatdetector
COPY requirements.txt /opt/pycatdetector

ENV PYTHONUNBUFFERED 1
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN --mount=type=cache,target=/root/.cache/pip pip3 install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -Ur requirements.txt
# RUN pip3 cache purge

# To fix conflict with PyTorch and MXNet requirements:
RUN sed -i 's/\(_require_.*_version(\)/# FIX: \1/g' \
    /opt/venv/lib/python3.10/site-packages/gluoncv/__init__.py

# Workaround to avoid downloading the models every time
# image is built or container is created from the image
COPY pycatdetector/AbstractNeuralNet.py /opt/pycatdetector/pycatdetector/
COPY pycatdetector/NeuralNetMXNet.py /opt/pycatdetector/pycatdetector/
COPY pycatdetector/NeuralNetPyTorch.py /opt/pycatdetector/pycatdetector/
COPY pycatdetector/Preloader.py /opt/pycatdetector/pycatdetector/
RUN python3 -c "from pycatdetector.Preloader import preload; preload()"

# This allows faster builds
COPY pycatdetector /opt/pycatdetector/pycatdetector
COPY main.py /opt/pycatdetector/

ENTRYPOINT [ "python3" , "main.py" ]
CMD [ "-c" ]
