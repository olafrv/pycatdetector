#!/usr/bin/make

# GitHub auth is read from the git credential helper (see `git config
# credential.helper`), populated by a normal `git push` to this repo's
# origin. The token needs `repo` + `write:packages` scopes (classic PAT)
# to cover git push, ghcr.io push, and the releases API alike.

NAME=$(shell cat METADATA | grep NAME | cut -d"=" -f2)
VERSION:=$(shell cat METADATA | grep VERSION | cut -d"=" -f2)
REPOSITORY="${NAME}"
GITHUB_USER:=$(shell git remote get-url origin | sed -E 's#.*github\.com[:/]+([^/]+)/.*#\1#')
IMAGE_NAME="ghcr.io/${GITHUB_USER}/${REPOSITORY}"
IMAGE_APP_DIR="/opt/${REPOSITORY}"
GITHUB_API="https://api.github.com/repos/${GITHUB_USER}/${REPOSITORY}"
GITHUB_API_JSON:=$(shell printf '{"tag_name": "%s","target_commitish": "main","name": "%s","body": "Version %s","draft": false,"prerelease": false}' ${VERSION} ${VERSION} ${VERSION})
CPUS=2

env:
	@ grep -q '@github.com' ~/.git-credentials 2>/dev/null \
		|| (echo "No GitHub credential cached. Run 'git push' once to cache one." && exit 1)

metadata: 
	@ echo "METADATA: NAME=${NAME}, VERSION=${VERSION}"

install: install.venv
	@ . venv/bin/activate \
		&& pip3 install -Ur requirements.txt

# customize!
install.dev: install.venv
	@ command -v patchelf >/dev/null || (echo "Missing patchelf. Install manually: sudo apt install patchelf" && exit 1)
	@ command -v ccache >/dev/null || (echo "Missing ccache. Install manually: sudo apt install ccache" && exit 1)
	@ . venv/bin/activate \
		&& pip3 install -Ur requirements-dev.txt

# customize!
install.venv: install.base
	@ true \
		&& test -d venv || python3 -m venv venv \
		&& . venv/bin/activate \
		&& pip3 install -Ur requirements.txt \
		&& pip3 install --upgrade pip

# Read-only prerequisite check (no sudo, no apt, no system mutation).
# Fails fast with an actionable message instead of installing anything,
# so `make test`/`make run`/etc. stay fast and don't silently require root.
install.base:
	@ command -v python3 >/dev/null || (echo "Missing python3. Install manually: sudo apt install python3" && exit 1)
	@ python3 -m venv --help >/dev/null 2>&1 || (echo "Missing python3-venv. Install manually: sudo apt install python3.12-venv" && exit 1)
	@ python3 -c "import ensurepip" 2>/dev/null || (echo "Missing python3-pip/ensurepip. Install manually: sudo apt install python3-pip" && exit 1)
	@ python3 -c "import tkinter" 2>/dev/null || (echo "Missing python3-tk. Install manually: sudo apt install python3-tk" && exit 1)
	@ command -v gcc >/dev/null || (echo "Missing build-essential/gcc. Install manually: sudo apt install build-essential gcc" && exit 1)
	@ command -v ffmpeg >/dev/null || (echo "Missing ffmpeg. Install manually: sudo apt install ffmpeg" && exit 1)
	@ command -v jq >/dev/null || (echo "Missing jq. Install manually: sudo apt install jq" && exit 1)

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
check-config: install.venv
	@ . venv/bin/activate \
		&& python3 main.py --check-config | jq

build: install.dev
	# https://nuitka.net/doc/user-manual.html
	# https://nuitka.net/info/debian-dist-packages.html (Work in ubuntu!)
	# python3 -m nuitka --standalone --onefile --enable-plugin=numpy -o ${NAME}.bin main.py
	@ . venv/bin/activate \
		&& python3 -m nuitka --include-package=${NAME} --output-dir=./build \
			--show-progress --report=./build/main.xml -j6 \
			main.py
	@ chmod +x build/main.bin

package.outdated: install.dev
	@ . venv/bin/activate \
		&& pip3 list --outdated > requirements.new && deactivate
	@ grep -f requirements.txt requirements.new > requirements.outdated || true
	@ grep -f requirements-dev.txt requirements.new > requirements-dev.outdated || true
	@ rm -f requirements.new && ls -ls *.outdated || true

# customize!
run: install.venv
	@ mkdir -p logs \
		&& . venv/bin/activate \
		&& python3 main.py

run.bin:
	@ ./build/main.bin

test: install.dev
	# https://docs.pytest.org/
	@ . venv/bin/activate \
		&& pytest -s --disable-warnings ${NAME}/tests/

# customize!
coverage: install.dev
	# https://coverage.readthedocs.io
	# The trap 'true' INT command tells the shell to ignore SIGINT (Ctrl+C) 
	# signals, prevents 'make' to stop after the GUI is closed.
	@ . venv/bin/activate \
	 	&& trap 'true' INT \
		&& coverage run main.py \
		&& coverage report --show-missing ${NAME}/*.py ${NAME}/channels/*.py

# customize!
coverage.test: install.dev
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
# Multiple architectures build (too slow for non native architectures)
#	@ if ! docker buildx ls | grep multi-arch-builder; \
#	then \
#		docker buildx create --name multi-arch-builder; \
#	fi
#	@ docker buildx build \
#		--push --platform linux/amd64,linux/arm64 \
#		-t ${IMAGE_NAME}:${VERSION} .
# Single architecture build (faster also the most used by end users)
	@ DOCKER_BUILDKIT=1 docker build -t ${IMAGE_NAME}:${VERSION} .
	@ docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest 

docker.clean:
	@ docker images | grep ${IMAGE_NAME} | awk '{print $$1":"$$2}' | sort | xargs --no-run-if-empty -n1 docker image rm

# customize!
docker.run:
	@ docker run --rm -it --cpus ${CPUS} --name ${NAME} \
		-v "${PWD}/config.yaml:${IMAGE_APP_DIR}/config.yaml:ro" \
    	-v "${PWD}/logs:${IMAGE_APP_DIR}/logs" \
		-v "${PWD}/videos:${IMAGE_APP_DIR}/videos" \
		-v "${PWD}/models:/root/.cache/torch" \
		${IMAGE_NAME}:${VERSION}

docker.start:
	@ docker compose pull && docker compose up -d

docker.sh:
	@ docker exec -it ${NAME} /bin/bash

docker.stop:
	@ docker compose down

docker.restart: docker.stop docker.start

github.formatter:
	black .

github.check_commit: github.formatter
	# Fail if uncommited changes
	git diff --exit-code
	git diff --cached --exit-code

github.build: github.check_commit docker.build

github.test: github.build test

github.push: github.test
	# https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
	# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
	# Token is pulled from the git credential store, not an env var.
	@ TOKEN=$$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p') \
		&& echo "$${TOKEN}" | docker login ghcr.io --username ${GITHUB_USER} --password-stdin \
		&& docker push ${IMAGE_NAME}:${VERSION} \
		&& docker push ${IMAGE_NAME}:latest

github.release: github.push
	# Create and push tag
	git tag -d ${VERSION} && git push --delete origin ${VERSION} || /bin/true
	git tag ${VERSION} && git push origin ${VERSION}
	# https://docs.github.com/rest/reference/repos#create-a-release
	@ TOKEN=$$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p') \
		&& echo '${GITHUB_API_JSON}' | curl \
			-H 'Accept: application/vnd.github+json' \
			-H "Authorization: token $${TOKEN}" \
			-d @- ${GITHUB_API}/releases
