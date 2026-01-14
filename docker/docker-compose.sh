#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set the current mode from the argument or default to "nowatch"
MODE=${1:-nowatch}

# Check if the first argument is a valid mode passed from the command line
if [ $# -ge 1 ]; then
  if [ "$1" == "watch" ] || [ "$1" == "nowatch" ]; then
    shift # Remove the mode argument so that $@ contains the rest
  fi
fi

# Validate the MODE parameter
if [ "$MODE" != "watch" ] && [ "$MODE" != "nowatch" ]; then
  echo "Error: Invalid mode '$MODE'. Valid modes are 'watch' or 'nowatch'."
  exit 1
fi

# Determine Dockerfile based on MODE
if [ "$MODE" == "watch" ]; then
  FILENAME="docker/local/Dockerfile.watch"
else
  FILENAME="docker/local/Dockerfile.nowatch"
fi

# Rebuild frontend service if MODE was changed
FRONTEND_DOCKERFILE=$FILENAME docker compose build frontend

# Run all services with the remaining arguments
docker compose "$@" up -d

