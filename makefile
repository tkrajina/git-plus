GIT_PORCELAIN_STATUS=$(shell git status --porcelain)

test: mypy
	# At least make sure simple commands run without errors:
	./git-multi status
	./git-old-branches  -d -1
	./git-recent
	./git-relation HEAD HEAD~5
mypy:
	for script in $(shell ls git-*); do mypy --strict $$script; done
check-all-commited:
	if [ -n "$(GIT_PORCELAIN_STATUS)" ]; \
	then \
	    echo 'YOU HAVE UNCOMMITED CHANGES'; \
	    git status; \
	    exit 1; \
	fi
pypi-upload: check-all-commited
	rm -Rf dist/*
	python setup.py sdist
	twine upload dist/*
ctags:
	ctags -R .
clean:
	rm -Rf build
	rm -Rf dist
	rm -Rf MANIFEST
pyflakes:
	pyflakes $(grep -r -l "/usr/bin/python" * */*) $(find . -name "*py")
