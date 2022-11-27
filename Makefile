NAME=pycatdetector
VERSION=1.0.0

install:
	apt install -y python3 \
    	&& apt install -y python3.10-venv\
    	&& apt install -y --no-install-recommends build-essential gcc \
    	&& apt install -y ffmpeg \
    	&& apt clean
	pip install -Ur requirements.txt

install.dev: install
	pip install -Ur requirements-dev.txt

run:
	python3 main.py

profile:
	# https://docs.python.org/3/library/profile.html
	python3 -m cProfile -o main.prof main.py

profile.view:
	snakeviz main.prof

docker.run:
	docker run --rm -it ${NAME}:${VERSION}

docker.exec:
	docker run --rm -it --entrypoint /bin/bash ${NAME}:${VERSION}

docker.build:
	docker build -t ${NAME}:${VERSION} .

docker.clean:
	docker images | grep ${NAME} | awk '{print $$1":"$$2}' | sort | xargs --no-run-if-empty -n1 docker image rm