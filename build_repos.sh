#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_COMMAND="${PYTHON:-python3}"
PACKAGE_MANAGER="${PACKAGE_MANAGER:-yarn}"

function echo_header() {
  echo
  echo "================================================================"
  echo " $1"
  echo "================================================================"
}

function build_main_backend() {
  echo_header "Main backend"
  if [[ ! -f "$ROOT_DIR/backend/requirements.txt" ]]; then
    echo "ERROR: backend/requirements.txt not found"
    return 1
  fi
  pushd "$ROOT_DIR/backend" > /dev/null
  echo "Installing Python dependencies for main backend..."
  "$PYTHON_COMMAND" -m pip install -r requirements.txt
  echo "Main backend dependency install complete."
  popd > /dev/null
}

function build_main_frontend() {
  echo_header "Main frontend"
  if [[ ! -f "$ROOT_DIR/frontend/package.json" ]]; then
    echo "ERROR: frontend/package.json not found"
    return 1
  fi
  pushd "$ROOT_DIR/frontend" > /dev/null
  echo "Installing node dependencies for main frontend..."
  "$PACKAGE_MANAGER" install
  echo "Building main frontend..."
  "$PACKAGE_MANAGER" build
  echo "Main frontend build complete."
  popd > /dev/null
}

function build_sla113_backend() {
  echo_header "SLA113 backend"
  if [[ ! -f "$ROOT_DIR/sla113_standalone/backend/requirements.txt" ]]; then
    echo "ERROR: sla113_standalone/backend/requirements.txt not found"
    return 1
  fi
  pushd "$ROOT_DIR/sla113_standalone/backend" > /dev/null
  echo "Installing Python dependencies for SLA113 backend..."
  "$PYTHON_COMMAND" -m pip install -r requirements.txt
  echo "SLA113 backend dependency install complete."
  popd > /dev/null
}

function build_sla113_frontend() {
  echo_header "SLA113 standalone frontend"
  if [[ ! -f "$ROOT_DIR/sla113_standalone/frontend/package.json" ]]; then
    echo "SKIPPED: sla113_standalone/frontend/package.json not found"
    echo "This repository contains only source files for the standalone frontend, not a complete Node project."
    echo "If you want to build this frontend, add a package.json and install the required React dependencies."
    return 0
  fi
  pushd "$ROOT_DIR/sla113_standalone/frontend" > /dev/null
  echo "Installing node dependencies for SLA113 standalone frontend..."
  "$PACKAGE_MANAGER" install
  echo "Building SLA113 standalone frontend..."
  "$PACKAGE_MANAGER" build
  echo "SLA113 standalone frontend build complete."
  popd > /dev/null
}

function export_sla113_standalone() {
  local output_dir="${2:-$ROOT_DIR/sla113_export}"

  echo_header "Export SLA113 standalone repo"

  if [[ ! -f "$ROOT_DIR/sla113_standalone/split_repo.sh" ]]; then
    echo "ERROR: sla113_standalone/split_repo.sh not found"
    return 1
  fi

  pushd "$ROOT_DIR" > /dev/null
  echo "Running sla113_standalone/split_repo.sh -> $output_dir"
  bash sla113_standalone/split_repo.sh "$output_dir"

  echo "Validating exported repository structure..."
  local missing=0
  for path in "$output_dir/backend/requirements.txt" "$output_dir/frontend" "$output_dir/docker-compose.yml" "$output_dir/README.md"; do
    if [[ ! -e "$path" ]]; then
      echo "  MISSING: $path"
      missing=1
    fi
  done

  if [[ "$missing" -ne 0 ]]; then
    echo "ERROR: Export validation failed. Please check the exported repo at $output_dir."
    popd > /dev/null
    return 1
  fi

  echo "Export validated successfully: $output_dir contains backend/, frontend/, docker-compose.yml, README.md"
  popd > /dev/null
}

function export_and_build_sla113_standalone() {
  local output_dir="${2:-$ROOT_DIR/sla113_export}"

  export_sla113_standalone "$1" "$output_dir"
  if [[ $? -ne 0 ]]; then
    return 1
  fi

  echo_header "Build exported SLA113 standalone repo"
  pushd "$output_dir" > /dev/null

  if [[ -f "backend/requirements.txt" ]]; then
    echo "Installing SLA113 backend dependencies in exported repo..."
    "$PYTHON_COMMAND" -m pip install -r backend/requirements.txt
  fi

  if [[ -f "frontend/package.json" ]]; then
    echo "Installing SLA113 frontend dependencies in exported repo..."
    pushd frontend > /dev/null
    "$PACKAGE_MANAGER" install
    echo "Building SLA113 frontend in exported repo..."
    "$PACKAGE_MANAGER" build
    popd > /dev/null
  else
    echo "WARNING: Exported frontend package.json not found, skipping frontend build."
  fi

  echo "Exported SLA113 standalone repo build complete."
  popd > /dev/null
}

function usage() {
  cat <<EOF
Usage: $(basename "$0") [command]

Commands:
  main-backend      Install dependencies for the main backend
  main-frontend     Install and build the main frontend
  sla113-backend    Install dependencies for the SLA113 standalone backend
  sla113-frontend   Install and build the SLA113 standalone frontend (if configured)
  sla113-standalone-export [dir]
                    Export SLA113 standalone repo and validate output
  sla113-standalone-export-and-build [dir]
                    Export SLA113 standalone repo, validate output, and build exported repo
  all               Run main-backend, main-frontend, sla113-backend, and sla113-frontend
  help              Show this help text

Environment variables:
  PYTHON           Python executable to use (default: python3)
  PACKAGE_MANAGER  Node package manager to use (default: yarn)
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

case "$1" in
  main-backend)
    build_main_backend
    ;;
  main-frontend)
    build_main_frontend
    ;;
  sla113-backend)
    build_sla113_backend
    ;;
  sla113-frontend)
    build_sla113_frontend
    ;;
  sla113-standalone-export)
    export_sla113_standalone "$@"
    ;;
  sla113-standalone-export-and-build)
    export_and_build_sla113_standalone "$@"
    ;;
  all)
    build_main_backend
    build_main_frontend
    build_sla113_backend
    build_sla113_frontend
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "ERROR: Unknown command '$1'"
    usage
    exit 1
    ;;
 esac
