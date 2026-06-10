#!/bin/bash

# Run ty type checking against the subset of files that are fully annotated.
#
# Add a file to TYPED_FILES once it has type hints throughout. CI invokes
# this script directly, so updates here are the single source of truth.
#
# Usage:
#   ./check_types.sh           # check all files in TYPED_FILES
#   ./check_types.sh wp1/foo.py  # check a specific file (overrides the list)

set -e

TYPED_FILES=(
  wp1/models/wp10/builder.py
  wp1/models/wp10/selection.py
  wp1/models/wp10/zim_file.py
  wp1/models/wp10/zim_schedule.py
  wp1/logic/builder.py
  wp1/logic/selection.py
  wp1/logic/zim_files.py
  wp1/logic/zim_schedules.py
  wp1/selection/abstract_builder.py
  wp1/selection/models/simple.py
  wp1/selection/models/petscan.py
  wp1/selection/models/sparql.py
  wp1/selection/models/wikiproject.py
  wp1/selection/models/book.py
  wp1/selection/models/combinator.py
  wp1/selection/models/combinator_test.py
)

if [ "$#" -gt 0 ]; then
  pipenv run ty check "$@"
else
  pipenv run ty check "${TYPED_FILES[@]}"
fi
