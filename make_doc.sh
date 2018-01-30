#!/bin/sh

rm studuino/*.pyc
cd docs
make clean
cd ..
rm -rf api/*

sphinx-apidoc -f -o docs/apis studuino
cd docs
make html
cd ../
