.PHONY: all test install publish coverage lint

all:
	@echo 'Available targets: install, test, publish, coverage, lint'

install:
	pip install -U -e .

test:
	python setup.py test

publish: README.md setup.py
	rm -f dist/*
	python setup.py bdist_wheel --universal
	twine upload dist/*
	git push --tags

coverage:
	coverage run --source qtilities setup.py test
	coverage report
	coverage html

lint:
	flake8 qtilities test
