#!/bin/sh

sphinx-apidoc -f -o docs/ studuino/
cd docs
make html
cd ../
