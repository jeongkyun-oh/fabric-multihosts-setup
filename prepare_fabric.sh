#!/bin/bash
set +e

apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

# install make
apt-get --assume-yes install make

# install gcc
apt-get --assume-yes install gcc

# install go
snap install go --classic

# install docker
snap install docker

if [ ! -d "/root/go/" ]; then
    mkdir -p /root/go
fi

if [ ! -d "/root/gopath/" ]; then
    mkdir -p /root/gopath
fi

if [ ! -d "/root/testnet/" ]; then
    mkdir -p /root/testnet
fi

echo "export GOROOT=/root/go" >> /etc/profile
echo "export GOPATH=/root/gopath" >> /etc/profile
echo "export PATH=$PATH:/root/gopath/bin" >> /etc/profile
source /etc/profile

# install hyperledger fabric
if [ ! -d "/root/src/github.com/hyperledger/" ]; then
    mkdir -p $GOPATH/src/github.com/hyperledger
fi
cd $GOPATH/src/github.com/hyperledger

if [ ! -d "fabric" ]; then
    git clone -b release-1.3 https://github.com/hyperledger/fabric
fi

cd $GOPATH/src/github.com/hyperledger/fabric
if [ ! -f "./.build/bin/peer" ]; then
    make peer
fi
if [ ! -f "./.build/bin/configtxgen" ]; then
    make configtxgen
fi
if [ ! -f "./.build/bin/cryptogen" ]; then
    make cryptogen
fi
if [ ! -f "./.build/bin/orderer" ]; then
    make orderer
fi

echo "export FABRIC_HOME=$GOPATH/src/github.com/hyperledger/fabric" >> /etc/profile
echo "export PATH=$PATH:$GOPATH/src/github.com/hyperledger/fabric/.build/bin" >> /etc/profile
source /etc/profile

cp $FABRIC_HOME/sampleconfig/core.yaml /root/testnet/core.yaml
cp $FABRIC_HOME/sampleconfig/orderer.yaml /root/testnet/orderer.yaml
echo "export FABRIC_CFG_PATH=/root/testnet" >> /etc/profile
source /etc/profile
