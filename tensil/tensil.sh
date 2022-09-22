#!/bin/bash

set -e
set -u
set -o pipefail

tag=1.0.15
tarch_file=tensil.tarch

if [ ! -f ./src/top_tensil.v ]; then
    docker run --user "$(id -u):$(id -g)" -v $(pwd):/work -w /work -it tensilai/tensil:$tag tensil rtl -a /work/$tarch_file -s true -d 128
    cp bram_dp_128x2048.v bram_dp_128x8192.v top_tensil.v src/
    rm bram_dp_128x2048.v bram_dp_128x8192.v top_tensil.v top_tensil.fir firrtl_black_box_resource_files.f top_tensil.anno.json architecture_params.h
fi
