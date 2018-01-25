#!/bin/sh

sphinx-apidoc -f -o docs/apis studuino
cd docs
make html
cd ../
