#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/setup.sh

if [[ $# -eq 0 ]]; then
  echo "usage: $0 [0-6]"
  echo "0: peer0"
  echo "1: peer1"
  echo "2: peer2"
  echo "3: peer3"
  echo "4: orderer0"
  echo "5: kafka-zookeeper"
  echo "6: client"
  exit 1
fi

fab login:$TAG_NAME,$1
