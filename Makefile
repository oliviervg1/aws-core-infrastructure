.PHONY: clean
clean:
	- rm -rf env
	- find . -name "*.pyc" | xargs rm

env/bin/activate:
	virtualenv env

requirements.txt: env/bin/activate
	. env/bin/activate && pip install -r requirements.txt

.PHONY: lint
lint:
	. env/bin/activate && flake8 stacks

.PHONY: infrastructure
infrastructure: requirements.txt lint
	. env/bin/activate && stacker build \
		-t \
		-r eu-west-2 \
		-e namespace=core \
		config/aws-core-infrastructure.env \
		config/aws-core-infrastructure.yaml
