#!/usr/bin/make

# Environment Variables:
# - GITHUB_USER
# - GITHUB_TOKEN

NAME=$(shell cat METADATA | grep NAME | cut -d"=" -f2)
VERSION:=$(shell cat METADATA | grep VERSION | cut -d"=" -f2)
REPOSITORY="${NAME}"
IMAGE_NAME="ghcr.io/${GITHUB_USER}/${REPOSITORY}"
IMAGE_APP_DIR="/opt/${REPOSITORY}"
GITHUB_API="https://api.github.com/repos/${GITHUB_USER}/${REPOSITORY}"
GITHUB_API_JSON:=$(shell printf '{"tag_name": "%s","target_commitish": "main","name": "%s","body": "Version %s","draft": false,"prerelease": false}' ${VERSION} ${VERSION} ${VERSION})
CPUS=2

env:
	@ env | grep -E "GITHUB_" || (echo "GITHUB_ variables not set." && exit 1)

metadata: 
	@ echo "METADATA: NAME=${NAME}, VERSION=${VERSION}"

install: install.venv
# https://github.com/pytorch/pytorch/issues/17023  - PyTorch Download Speed Issue
	@ . venv/bin/activate \
		&& pip3 install -Ur requirements.txt

# customize!
install.dev: install.venv
	@ . venv/bin/activate \
		&& pip3 install -Ur requirements-dev.txt \
		&& sudo apt install -y patchelf ccache

# customize!
install.venv: install.base
	@ true \
		&& test -d venv || python3 -m venv venv \
		&& . venv/bin/activate \
		&& pip3 install -Ur requirements.txt \
		&& pip3 install --upgrade pip \
		&& sed -i 's/\(_require_.*_version(\)/# FIX: \1/g' venv/lib/python3.10/site-packages/gluoncv/__init__.py \
		&& python3 -c "from pycatdetector.Preloader import preload; preload()"


install.base:
	@ sudo apt update \
		&& sudo apt install -y python3 \
		&& sudo apt install -y python3.10-venv python3-dev python3-setuptools \
		&& sudo apt install -y --no-install-recommends build-essential gcc \
		&& sudo apt install -y python3-pip \
		&& sudo apt install python3-tk  # matplotlib uses tkinter

uninstall: uninstall.venv clean

uninstall.venv: 
	#pip3 list --user --format=freeze | sed 's/=.*$//' | xargs pip3 uninstall --yes
	#@ test ! -d env \
	#	|| . venv/bin/activate \
	#	&& pip3 uninstall --yes -r requirements.txt \
	#	&& pip3 uninstall --yes -r requirements-dev.txt
	rm -rf venv

# customize!
clean:
	@ rm -rf build logs

# customize!
check-config:
	@ . venv/bin/activate \
		&& python3 main.py --check-config

build: install.dev
	# https://nuitka.net/doc/user-manual.html
	# https://nuitka.net/info/debian-dist-packages.html (Work in ubuntu!)
	# python3 -m nuitka --standalone --onefile --enable-plugin=numpy -o ${NAME}.bin main.py
	@ . venv/bin/activate \
		&& python3 -m nuitka --include-package=${NAME} --output-dir=./build \
			--show-progress --report=./build/main.xml -j6 \
			main.py
	@ chmod +x build/main.bin

package.outdated:
	@ . venv/bin/activate \
		&& pip3 list --outdated > requirements.new && deactivate
	@ grep -f requirements.txt requirements.new > requirements.outdated || true
	@ grep -f requirements-dev.txt requirements.new > requirements-dev.outdated || true

# customize!
run:
	@ mkdir -p logs \
		&& . venv/bin/activate \
		&& python3 main.py

run.bin:
	@ ./build/main.bin

test:
	# https://docs.pytest.org/
	@ . venv/bin/activate \
		&& pytest -s --disable-warnings ${NAME}/tests/

# customize!
test.coverage:
	# https://coverage.readthedocs.io
	@ . venv/bin/activate \
		&& coverage run main.py \
		&& coverage report --show-missing ${NAME}/*.py ${NAME}/channels/*.py

# customize!
test.coverage.report:
	@ . venv/bin/activate \
		&& coverage run -m pytest -s --disable-warnings ${NAME}/tests/ \
		&& coverage report --show-missing ${NAME}/*.py ${NAME}/channels/*.py

profile: install.dev
	# https://docs.python.org/3/library/profile.html
	@ mkdir -p profile \
		&& . venv/bin/activate \
		&& python3 -m cProfile -o profile/main.prof main.py

profile.view: install.dev
	@ . venv/bin/activate && snakeviz profile/main.prof

docker.build:
# ARM64 MXNet Issue Impides Multi-Arch Build: 
# https://github.com/apache/mxnet/issues/19234
#	@ if ! docker buildx ls | grep multi-arch-builder; \
#	then \
#		docker buildx create --name multi-arch-builder; \
#	fi
#	@ docker buildx build \
#		--push --platform linux/amd64,linux/arm64 \
#		-t ${IMAGE_NAME}:${VERSION} .
	@ DOCKER_BUILDKIT=1 docker build -t ${IMAGE_NAME}:${VERSION} .
	@ docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest 

docker.clean:
	@ docker images | grep ${IMAGE_NAME} | awk '{print $$1":"$$2}' | sort | xargs --no-run-if-empty -n1 docker image rm

# customize!
docker.run:
	@ docker run --rm -it --cpus ${CPUS} \
		-v "${PWD}/config.yaml:${IMAGE_APP_DIR}/config.yaml:ro" \
    	-v "${PWD}/logs:${IMAGE_APP_DIR}/logs" \
		-v "${PWD}/videos:${IMAGE_APP_DIR}/videos" \
		${IMAGE_NAME}:${VERSION}

docker.start:
	@ docker compose pull && docker compose up -d

docker.sh:
	@ docker exec -it ${NAME} /bin/bash

docker.stop:
	@ docker compose down

docker.restart: docker.stop docker.start

github.push: docker.build
	# https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
	# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
	# https://docs.github.com/en/actions/security-guides/automatic-token-authentication#about-the-github_token-secret
	@ echo ${GITHUB_TOKEN} | docker login ghcr.io --username ${GITHUB_USER} --password-stdin
	@ docker push ${IMAGE_NAME}:${VERSION}
	@ docker push ${IMAGE_NAME}:latest

github.release: github.push
	# Fail if uncommited changes
	git diff --exit-code
	git diff --cached --exit-code
	# Create and push tag
	git tag -d ${VERSION} && git push --delete origin ${VERSION} || /bin/true
	git tag ${VERSION} && git push origin ${VERSION}
	# https://docs.github.com/rest/reference/repos#create-a-release
	@echo '${GITHUB_API_JSON}' | curl \
		-H 'Accept: application/vnd.github+json' \
		-H 'Authorization: token ${GITHUB_TOKEN}' \
		-d @- ${GITHUB_API}/releases
