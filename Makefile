NAME=olafrv/pycatdetector
VERSION=1.1.0

install:
	sudo apt install -y python3 \
    	&& sudo apt install -y python3.10-venv\
    	&& sudo apt install -y --no-install-recommends build-essential gcc \
    	&& sudo apt install -y ffmpeg \
    	&& sudo apt install patchelf
		&& sudo apt clean
	pip install -Ur requirements.txt

install.dev: install
	pip install -Ur requirements-dev.txt

run:
	python3 main.py

bin:
	# https://nuitka.net/doc/user-manual.html
	# https://nuitka.net/info/debian-dist-packages.html (Work in ubuntu!)
	# python3 -m nuitka --standalone --onefile --enable-plugin=numpy -o pycatdetector.bin main.py
	python3 -m nuitka --include-package=pycatdetector --output-dir=./build \
		--show-progress --report=pycatdetector.bin.txt -j6 -o ./pycatdetector.bin \
		main.py

	chmod +x pycatdetector.bin
	./pycatdetector.bin

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
	docker build -t ${NAME}:latest .
	docker tag ${NAME}:latest ${NAME}:${VERSION}

docker.push:
	docker push ${NAME}:latest
	docker push ${NAME}:${VERSION}

docker.clean:
	docker images | grep ${NAME} | awk '{print $$1":"$$2}' | sort | xargs --no-run-if-empty -n1 docker image rm