#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/setup.sh

fab create_instance_with_fabric_image:7,$TAG_NAME
