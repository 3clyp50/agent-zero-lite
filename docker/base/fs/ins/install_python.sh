#!/bin/bash
set -e

echo "====================PYTHON START===================="

echo "====================PYTHON 3.12 VENV===================="

# create and activate the shared runtime venv
python -m venv /opt/venv
source /opt/venv/bin/activate

# upgrade pip and install static packages
pip install --no-cache-dir --upgrade pip pipx ipython requests

echo "====================PYTHON UV ===================="

curl -Ls https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh

# clean up pip cache
pip cache purge

echo "====================PYTHON END===================="
