#!/bin/bash

set -e
set -u
set -o pipefail

# create deploy dir
if [ ! -d ./deploy ]; then
    mkdir deploy
fi


# get cifar dataset
if [ ! -d ./deploy/test_batch ]; then
    wget http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz
    tar xfvz cifar-10-python.tar.gz
    rm cifar-10-batches-py/data_batch_*
    cp -r cifar-10-batches-py/* deploy
    rm -r cifar-10-batches-py
    rm cifar-10-python.tar.gz
fi
