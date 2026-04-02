#!/bin/bash

# start webapp
cd /usr/local/searxng/searxng-src
export SEARXNG_SETTINGS_PATH="/etc/searxng/settings.yml"

# activate the shared runtime venv
source "/opt/venv/bin/activate"

exec python /usr/local/searxng/searxng-src/searx/webapp.py
