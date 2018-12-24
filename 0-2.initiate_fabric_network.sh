#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/setup.sh

fab get_hosts:$AWS_FABRIC_IMAGE_NAME initiate_fabric_network
