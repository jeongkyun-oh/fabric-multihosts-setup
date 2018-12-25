# Hyperledger Fabric Multihosts Setup with AWS

This repository explains how to setup Hyperledger Fabric multi-hosts network setup using AWS.
<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Hyperledger Fabric Multihosts Setup with AWS](#hyperledger-fabric-multihosts-setup-with-aws)
	- [Prerequisites](#prerequisites)
	- [Scenario](#scenario)
		- [Build an AWS image installed with required applications](#build-an-aws-image-installed-with-required-applications)
		- [Build a private network](#build-a-private-network)
			- [Run peer0, 1, 2, and 3](#run-peer0-1-2-and-3)
			- [Run orderer0](#run-orderer0)
			- [Launch Kafka-Zookeeper docker container](#launch-kafka-zookeeper-docker-container)
			- [Create a channel](#create-a-channel)
			- [Join peers into the channel](#join-peers-into-the-channel)
			- [Install a chaincode](#install-a-chaincode)
			- [Instantiate the chaincode](#instantiate-the-chaincode)
			- [Query](#query)
			- [Invoke](#invoke)
			- [Terminate](#terminate)
	- [Author](#author)

<!-- /TOC -->

## Prerequisites
* [Python](https://www.python.org/)
* [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [Fabric](http://www.fabfile.org/)
* [AWS CLI](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-chap-install.html)

You need to configure your environment with `aws configure` beforehand. Please check out [AWS CLI configuration](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-chap-configure.html).
You may need to change the environment variables of `setup.sh` file. The variables are self-explanatory.

## Scenario
This network consists of several stakeholders as follows.
- Organization0
    - Peer0, Peer1
- Organization 1
    - Peer2, Peer3
- Orderer Organization
    - Orderer0
- Kafka-Zookeeper Docker Container
- Client

Note: we uses `cryptogen` for all credentials (for development purpose) instead of certificate authorities (for production level) so that the client has all the power in order to create a channel, join peers, install a chaincode, and so on.

### Build an AWS image installed with required applications
We are going to launch a default ubuntu 18.04 image and install necessary softwares on the top of the instance with the following command.
```
$ ./0-0.prepare_fabric_instance.sh
```
Once a new instance is running (it may need to take a few minutes), it is necessary to install some softwares.
The required softwares are as follows:
* Golang
* GCC
* Make
* Docker
* Docker Compose
* Hyperledger Fabric 1.3 modules (peer, orderer, cryptogen, configtxgen)

The following command line will install the above softwares on the running instance.
```
$ ./0-1.initiate_fabric_instance.sh
```
Now, we are ready to build a private network with Hyperledger Fabric modules. As mentioned earlier, we are going to use `cryptogen` to create all required credentials. All nodes have to have the credentials to access each other node. The created credentials are not necessary to be distributed to all peers, but we do this for convenience. The predefined script files under the `script` folder will be uploaded. The following command line will do all these.
```
$ ./0-2.initiate_fabric_network.sh
```
We need to clone the instance at this point. Hence, we store the current instance as an AMI with the following command line.
Note: it may take a few minutes to create the image.
```
$ ./0-3.create_fabric_image.sh
```
After the new image is created, we do not need the running instance. The following command line will terminate the current running instance.
```
$ ./0-4.terminate_fabric_image.sh
```

### Build a private network
In the previous section, a new prepared image was created. We need to launch 7 instances initiated by the image that we just created.
In order to create instances, please do the following command. Note: it may require a few minutes to launch instances.
```
$ ./1.create_instances.sh
```
The instance needs to know each other IP addresses. The following command line will upload and set up `hosts` on each instance to communicate with each other.
```
$ ./2.init_instance.sh
```

Prepare 7 terminal tabs to enter into each instance and do the following command line on each tab. Note: `<num>` is from `0` to `6`.
(`0`: peer0, `1`: peer1, `2`: peer2, `3`: peer3, `4`: orderer0, `5`: kafka-zookeeper, `6`: client)
```
$ ./login.sh <num>
```

The `testnet` is installed with sudo mode. On each terminal tab, do the following command lines.
```
$ sudo -i
$ cd /root/testnet/
```

#### Run peer0, 1, 2, and 3
First, we launch peer modules on `peer0`, `peer1`, `peer2` and `peer3`. For example, do the following command for `peer0`.
```
$ ./script/runPeer0.sh
```
#### Run orderer0
Let's launch orderer0 as follows for `orderer0`. In order to launch `orderer0`, a genesis block having a network configuration is needed. The following command lines will create the `genesis.block` and launch `orderer0` consecutively. Checkout the network configuration in `configtx.yaml`.
```
$ ./script/createGenesisBlock.sh
$ ./script/runOrderer0.sh
```

#### Launch Kafka-Zookeeper docker container
Firstly, we launch kafka-zookeeper docker container as following command line.
```
$ cd ./script
$ docker-compose up
```

#### Create a channel
In order to send a transaction, a channel must be created. In order to do this, the new channel configuration transaction is required to be sent to the orderer. The following command line creates a channel configuration transansaction `ch1.tx`. Next, it will send the `ch1.tx` to the orderer resulting in `ch1.block` which is a genesis block for the created channel. The channel configuration is described in `configtx.yaml`
```
$ ./script/createChannelTx.sh
$ ./script/create-channel.sh
```

#### Join peers into the channel
After a channel creation, peers need to join the channel. The following command line is an example in order for `peer0` to join the channel `ch1`. The joining peer on the channel requires the channel genesis block `ch1.block`.
```
$ ./script/peer0-join.sh
```

#### Install a chaincode
After all peers joined the channel `ch1`, let's install a chaincode on each peer. Installing a chaincode on `peer0` is as follows.
Note: we do not need to install the chaincode on all peer nodes. Installing it on peer0 is enough to do chaincode instantiation and sending transactions.
The chaincode is a basic chaincode which hyperledger fabric provides with. After the initiation, `A` holds 100 and `B` holds 200.
The chaincode is in `/root/gopath/src/github.com/hyperledger/fabric/examples/chaincode/go/example02/cmd`.
```
$ ./script/installCCpeer0.sh
```

#### Instantiate the chaincode
The following command line instantiates the chaincode on the channel.
Note: you must install the chaincode on `peer0` at least before.
```
$ ./script/instantitateCC.sh
```

#### Query
The following command line will query the amount of the asset `B`.
```
$ ./script/query.sh
```

#### Invoke
The following command line will do a transaction sending `20` from `A` to `B`.
```
$ ./script/invoke.sh
```

#### Terminate
Once you are done with playing around with the network, you can terminate all instances on your local terminal with the following command.
```
$ ./3.terminate_instances.sh
```

## Author
If you have any question, please do not hesitate to contact me.

* jk.oh@groundx.xyz

The network setup script files are derived from [Jpub/Hyperledger](https://github.com/Jpub/HyperLedger).
Modified and improved for this repository.
