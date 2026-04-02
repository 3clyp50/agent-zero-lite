#!/bin/bash
set -e

echo "====================SEARXNG2 START===================="

# clone SearXNG repo
git clone "https://github.com/searxng/searxng" \
                   "/usr/local/searxng/searxng-src"

echo "====================SEARXNG2 SHARED VENV===================="

# use the shared runtime environment
source "/opt/venv/bin/activate"
echo ". /opt/venv/bin/activate" > "/usr/local/searxng/.profile"

echo "====================SEARXNG2 INST===================="

# update pip's boilerplate
pip install --no-cache-dir -U pip setuptools wheel pyyaml lxml msgspec typing_extensions

# jump to SearXNG's working tree and install SearXNG into virtualenv
cd "/usr/local/searxng/searxng-src"
# pip install --no-cache-dir --use-pep517 --no-build-isolation -e .
pip install --no-cache-dir --use-pep517 --no-build-isolation .

# cleanup cache
pip cache purge

chown -R "searxng:searxng" "/usr/local/searxng"

echo "====================SEARXNG2 END===================="
