#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/setup.sh

fab create_instance:1,$AWS_FABRIC_IMAGE_NAME
