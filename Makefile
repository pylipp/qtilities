VERSION=$(shell python -c 'import qtilities; print(qtilities.__version__)')

.PHONY: all test install tags upload tag publish coverage lint

all:
	@echo 'Available targets: install, test, upload, tag, publish, coverage, lint'

install:
	pip install -U -e .

test:
	python setup.py test

upload: README.md setup.py
	rm -f dist/*
	python setup.py bdist_wheel --universal
	twine upload dist/*

tag:
	git tag v$(VERSION)
	git push --tags

publish: tag upload

coverage:
	coverage run --source qtilities setup.py test
	coverage report
	coverage html

lint:
	flake8 qtilities test
