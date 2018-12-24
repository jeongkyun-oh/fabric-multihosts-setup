#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/setup.sh

fab terminate_instances:$AWS_FABRIC_IMAGE_NAME
