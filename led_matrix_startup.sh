#!/bin/bash

PROJECT_ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "System Starting Up LED Matrix
cd ${PROJECT_ROOT_DIR}/
sudo /usr/bin/python3 ${PROJECT_ROOT_DIR}/run.py &