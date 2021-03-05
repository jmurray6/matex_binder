#!/bin/bash
# Change conda environment
source $(dirname $CONDA_EXE)/../etc/profile.d/conda.sh

conda activate asscomp

# Activate error management
set -eu

python main.py

