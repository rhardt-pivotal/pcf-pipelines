#!/bin/bash

set -euo pipefail

cd pcf-pipelines/tasks/apply-vm-extensions-srt

pip install -r requirements.txt

python vmext_creator.py

