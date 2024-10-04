#!/usr/bin/env bash

PARENT_PATH=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
EXAMPLE_PATH=$(dirname "$PARENT_PATH")
TQEC_PATH=$(dirname "$EXAMPLE_PATH")
ASSETS_PATH=$(dirname "$TQEC_PATH")

tqec dae2observables "${ASSETS_PATH}/logical_cnot.dae" \
  --out-dir out
