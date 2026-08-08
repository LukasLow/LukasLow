.PHONY: icons

icons:
	docker run --rm \
		-v "$$(PWD):/workspace" \
		-w /workspace \
		python:3-slim \
		sh -c "apt-get update && apt-get install -y librsvg2-bin && pip install -r bildchen/scripts/requirements.txt && python bildchen/scripts/generate_icons.py"
