.PHONY: clean
clean:
	- rm -rf env
	- find . -name "*.pyc" | xargs rm

env/bin/activate:
	virtualenv env

requirements: env/bin/activate requirements.txt
	. env/bin/activate && pip install -r requirements.txt

.PHONY: lint
lint:
	. env/bin/activate && flake8 stacks

.PHONY: infrastructure
infrastructure: requirements lint
	. env/bin/activate && stacker build \
		-t \
		-r eu-west-2 \
		-e namespace=kubernetes \
		config/aws-core-infrastructure.env \
		config/aws-core-infrastructure.yaml
