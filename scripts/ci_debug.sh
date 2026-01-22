#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo "CI Pipeline Debugging Script"
echo "========================================="

check_python_environment() {
  echo "Checking Python environment..."
  echo "Python version: $(python --version 2>&1)"
  echo "Pip version: $(pip --version 2>&1)"
  echo "Python path: $(command -v python)"
  echo "Pip path: $(command -v pip)"
  echo ""
}

verify_requirements() {
  echo "Verifying requirements installation..."

  if [[ -f "requirements/base.txt" ]]; then
    echo "Found requirements/base.txt"
    echo "Attempting to install requirements..."
    pip install -r requirements/base.txt
    echo "✓ Requirements installed successfully"
  else
    echo "⚠ requirements/base.txt not found"
    return 1
  fi
  echo ""
}

check_test_environment() {
  echo "Checking test environment..."

  if command -v pytest &> /dev/null; then
    echo "✓ pytest is installed"
  else
    echo "Installing pytest..."
    pip install pytest
  fi

  if [[ -d "tests" || -d "test" ]]; then
    echo "✓ Test directory found"
  else
    echo "⚠ No test directory found"
  fi

  echo ""
}

run_tests_verbose() {
  echo "Running tests with verbose output..."

  if command -v pytest &> /dev/null; then
    pytest --verbose --tb=long
  else
    echo "pytest not available, trying python -m unittest..."
    python -m unittest discover -v
  fi

  echo ""
}

check_common_issues() {
  echo "Checking for common CI issues..."

  echo "Disk space usage:"
  df -h

  echo "Memory usage:"
  free -h

  echo "Looking for error logs..."
  find . -name "*.log" -type f 2>/dev/null | head -5

  echo ""
}

apply_common_fixes() {
  echo "Applying common fixes..."

  echo "Upgrading pip..."
  python -m pip install --upgrade pip

  echo "Clearing pip cache..."
  pip cache purge 2>/dev/null || echo "Pip cache command not available"

  echo "Installing/upgrading setuptools and wheel..."
  pip install --upgrade setuptools wheel

  echo ""
}

main() {
  check_python_environment
  check_common_issues
  apply_common_fixes
  verify_requirements

  check_test_environment
  echo "Setup completed successfully. You can now run your tests."
}

main

echo "========================================="
echo "Debug script completed"
echo "========================================="
