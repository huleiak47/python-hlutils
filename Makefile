ifeq ($(OS),Windows_NT)
	SHELL := cmd.exe
else
	SHELL := /bin/sh
endif

VERSION := $(shell python -c "import hlutils;print(hlutils.__version__)")
WHEEL := dist/hlutils-$(VERSION)-py3-none-any.whl

$(WHEEL): setup.py hlutils/*.py hlutils/tools/*.py hlutils/tools/*.html
	python setup.py bdist_wheel

install: $(WHEEL)
	-pip uninstall -y hlutils
	pip install $(WHEEL)

clean:
	rm -r build dist hlutils.egg-info
