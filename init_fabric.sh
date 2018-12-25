#!/bin/bash
source /etc/profile
cd /root/testnet
mv ./script/crypto-config.yaml ./
mv ./script/configtx.yaml ./
cryptogen generate --config=./crypto-config.yaml
