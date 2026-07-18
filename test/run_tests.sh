#!/bin/sh
# Self-test: strong fixture must pass (exit 0), weak must fail (exit 1),
# missing file must exit 2. Run from the repo root: sh test/run_tests.sh
set -e
cd "$(dirname "$0")/.."

python3 constitution_lint.py test/fixtures/strong/CONSTITUTION.md >/dev/null \
  || { echo "FAIL: strong fixture should exit 0"; exit 1; }

if python3 constitution_lint.py test/fixtures/weak/CONSTITUTION.md >/dev/null; then
  echo "FAIL: weak fixture should exit 1"; exit 1
fi

code=0
python3 constitution_lint.py test/fixtures/does-not-exist.md >/dev/null 2>&1 || code=$?
[ "$code" -eq 2 ] || { echo "FAIL: missing file should exit 2, got $code"; exit 1; }

echo "all tests pass"
