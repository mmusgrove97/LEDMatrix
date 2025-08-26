#!/bin/bash

PROJECT_ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "System Starting Up LED Matrix
sudo /usr/bin/python3 ${PROJECT_ROOT_DIR}/run.py &