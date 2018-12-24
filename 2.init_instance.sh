#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/setup.sh

fab write_hosts_file:$TAG_NAME
fab upload_hosts:$TAG_NAME
