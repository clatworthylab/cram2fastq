#!/bin/bash
set -e

CRAM_PATH=${1?Error: no cram path provided}

parallel cramfastq_bulk.sh ::: ${CRAM_PATH}/*.cram
