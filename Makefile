USERNAME=olafrv
NAME=ghcr.io/${USERNAME}/pycatdetector
VERSION=1.1.0
CPUS=2

install: install.venv
	@ . venv/bin/activate \
		&& pip3 install -Ur requirements.txt

install.dev: install.venv
	@ . venv/bin/activate \
		&& pip3 install -Ur requirements-dev.txt \
		&& sudo apt install -y patchelf ccache

install.venv: install.base
	@ test -d venv \
		|| python3 -m venv venv \
		&& pip3 install -Ur requirements.txt \
    	&& pip3 install --upgrade pip \
		&& python3 -c "from pycatdetector import NeuralNet; NeuralNet()";

install.base:
	@ sudo apt install -y python3 \
    	&& sudo apt install -y python3.10-venv\
    	&& sudo apt install -y --no-install-recommends build-essential gcc \
    	&& sudo apt install -y ffmpeg \
		&& sudo apt clean

uninstall: uninstall.venv clean

uninstall.venv: 
	# pip3 list --user --format=freeze | sed 's/=.*$//' | xargs pip3 uninstall --yes
	@ test ! -d env \
		|| . venv/bin/activate \
		&& pip3 uninstall --yes -r requirements.txt \
		&& pip3 uninstall --yes -r requirements-dev.txt

clean:
	@ rm -rf build __pycache__ venv

check-config:
	@ . venv/bin/activate \
		&& python3 main.py --check-config
run:
	@ mkdir -p logs \
		&& . venv/bin/activate \
		&& python3 main.py

run.bin:
	@ ./build/main.bin

build: install.dev
	# https://nuitka.net/doc/user-manual.html
	# https://nuitka.net/info/debian-dist-packages.html (Work in ubuntu!)
	# python3 -m nuitka --standalone --onefile --enable-plugin=numpy -o pycatdetector.bin main.py
	@ . venv/bin/activate \
		&& python3 -m nuitka --include-package=pycatdetector --output-dir=./build \
			--show-progress --report=./build/main.xml -j6 \
			main.py
	@ chmod +x build/main.bin

profile: install.dev
	# https://docs.python.org/3/library/profile.html
	@ mkdir -p profile \
		&& . venv/bin/activate
		&& python3 -m cProfile -o profile/main.prof main.py

profile.view: install.dev
	@ . venv/bin/activate && snakeviz profile/main.prof

docker.run:
	@ docker run --rm --cpus ${CPUS} \
		-v "${PWD}/config.yaml:/opt/pycatdetector/config.yaml:ro" \
    	-v "${PWD}/logs:/opt/pycatdetector/logs" \
		${NAME}:${VERSION}

docker.exec:
	@ docker run --rm -it --cpus ${CPUS} \
		-v "${PWD}/config.yaml:/opt/pycatdetector/config.yaml:ro" \
    	-v "${PWD}/logs:/opt/pycatdetector/logs" \
		--entrypoint /bin/bash ${NAME}:${VERSION}

docker.build:
	@ docker build -t ${NAME}:latest .
	@ docker tag ${NAME}:latest ${NAME}:${VERSION}

docker.push:
	# Personal Access Token (PAT) from GitHub
	# https://github.com/features/packages
	echo ${PAT} | docker login ghcr.io --username ${USERNAME} --password-stdin
	@ docker push ${NAME}:latest
	@ docker push ${NAME}:${VERSION}

docker.clean:
	@ docker images | grep ${NAME} | awk '{print $$1":"$$2}' | sort | xargs --no-run-if-empty -n1 docker image rm