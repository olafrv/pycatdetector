USERNAME=olafrv
NAME=ghcr.io/${USERNAME}/pycatdetector
VERSION:=$(shell cat VERSION)
API_JSON:=$(shell printf '{"tag_name": "%s","target_commitish": "main","name": "%s","body": "Release of version %s","draft": false,"prerelease": false}' ${VERSION} ${VERSION} ${VERSION})
CPUS=2

version:
	@ echo ${VERSION}

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
    	&& sudo apt install -y python3-tk ffmpeg \
		&& sudo apt clean

uninstall: uninstall.venv clean

uninstall.venv: 
	# pip3 list --user --format=freeze | sed 's/=.*$//' | xargs pip3 uninstall --yes
	#@ test ! -d env \
	#	|| . venv/bin/activate \
	#	&& pip3 uninstall --yes -r requirements.txt \
	#	&& pip3 uninstall --yes -r requirements-dev.txt
	rm -rf venv

clean:
	@ rm -rf build logs

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

test:
	@ . venv/bin/activate \
		&& pytest -s -s --disable-warnings pycatdetector/tests/

coverage:
	@ . venv/bin/activate \
		&& coverage run -m pytest -s --disable-warnings pycatdetector/tests/ \
		&& coverage report --show-missing pycatdetector/*.py pycatdetector/channels/*.py

coverage.live:
	@ . venv/bin/activate \
		&& coverage run main.py \
		&& coverage report --show-missing pycatdetector/*.py pycatdetector/channels/*.py


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
	@ docker build -t ${NAME}:${VERSION} .
	@ docker tag ${NAME}:${VERSION} ${NAME}:latest 

docker.push:
	# Personal Access Token (PAT) from GitHub
	# https://github.com/settings/tokens
	# https://github.com/features/packages
	echo ${GITHUB_PAT} | docker login ghcr.io --username ${USERNAME} --password-stdin
	@ docker push ${NAME}:${VERSION}
	@ docker push ${NAME}:latest

docker.clean:
	@ docker images | grep ${NAME} | awk '{print $$1":"$$2}' | sort | xargs --no-run-if-empty -n1 docker image rm

github.release:
	# Uncommited changes?
	git diff --exit-code
	git diff --cached --exit-code
	# Create and push tag
	git tag -d ${VERSION} && git push --delete origin ${VERSION} || /bin/true
	git tag ${VERSION} && git push origin ${VERSION}
	# https://docs.github.com/rest/reference/repos#create-a-release
	@echo '${API_JSON}' | curl -H "Accept: application/vnd.github+json" -H 'Authorization: token ${GITHUB_PAT}' -d @- https://api.github.com/repos/olafrv/pycatdetector/releases
