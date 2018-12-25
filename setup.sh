#!/bin/bash

## GENERAL OPTION
export TAG_NAME="jk"

## AWS SETUP
export AWS_FABRIC_IMAGE_NAME="fabric-init-instance"
export AWS_KEY_PATH="~/.ssh/jkoh.pem"
export AWS_KEY_NAME="jk.oh"
export AWS_SECURITY_GROUP="default"
export AWS_IMAGE_ID="ami-06e7b9c5e0c4dd014" # default ubuntu 18.04 image = ami-06e7b9c5e0c4dd014
export AWS_INSTANCE_TYPE="c4.2xlarge"
