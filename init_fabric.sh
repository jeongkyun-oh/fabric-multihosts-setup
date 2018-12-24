#!/bin/bash
source /etc/profile
cd /root/testnet
mv ./script/crypto-config.yaml ./
mv ./script/configtx.yaml ./
cryptogen generate --config=./crypto-config.yaml
configtxgen -profile TwoOrgsOrdererGenesis -outputBlock genesis.block
mv genesis.block /root/testnet/crypto-config/ordererOrganizations/ordererorg0/orderers/orderer0.ordererorg0/
configtxgen -profile TwoOrgsChannel -outputCreateChannelTx ch1.tx -channelID ch1
