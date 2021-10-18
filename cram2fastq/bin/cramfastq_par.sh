#!/bin/bash
set -e

CRAM_PATH=${1?Error: no cram path provided}

parallel cramfastq.sh ::: ${SAMPLE_LIST}/*.cram
