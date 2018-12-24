# Hyperledger Fabric Multihosts Setup with AWS

This repository explains how to setup Hyperledger Fabric multi-hosts network setup using AWS.



## Prerequisites
* [Python](https://www.python.org/)
* [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [Fabric](http://www.fabfile.org/)
* [AWS CLI](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-chap-install.html)

You need to configure your environment with `aws configure` beforehand. Please checkout [AWS CLI configuration](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-chap-configure.html)
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
* golang
* gcc
* make
* docker
* hyperledger fabric 1.3

The following command line will install the above softwares on the running instance.
```
$ ./0-1.initiate_fabric_instance.sh
```
Now, we are ready to build a private network with Hyperledger Fabric modules. As mentioned earlier, we are going to use `cryptogen` to create all required credentials. Furthermore, we are going to distribute `genesis.block` and `ch1.tx` as well. `genesis.block` is a genesis block for the orderer which contains the network configuration. `ch1.tx` is a configuration transaction for a channel creation. The predefined script will be uploaded in this phase under the `script` folder. The following command line will do this.
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
In the previous section, a new prepared image is created. We need to launch 7 instances initiated by the image that we just created.
In order to create instances, please do the following command. Note: it may require a few minutes to launch instances.
```
$ ./1.create_instances.sh
```
The instance needs to know each other IP address. The following command line will upload and set up `hosts` on each instance.
```
$ ./2.init_instance.sh
```

Prepare 7 tabs to enter into each instance and do the following command line on each tab. Note: `<num>` is from 0 to 6.
(0: peer0, 1: peer1, 2: peer2, 3: peer3, 4: orderer0, 5: kafka-zookeeper, 6: client)
Note: the number specifies each tab number.
```
$ ./login.sh <num>
```

The `testnet` is installed with sudo mode. On each tab, do the following command line.
```
$ sudo -i
$ cd /root/testnet/
```
#### Run peer0, 1, 2, 3
First, we launch peer modules from tab 0 to 3. For example, do the following command for tab 0.
```
$ ./script/runPeer0.sh
```
#### Run orderer0
Let's launch orderer0 as follows on tab 4.
```
$ ./script/runOrderer0.sh
```

#### Launch Kafka-Zookeeper docker container
Firstly, we launch kafka-zookeeper docker container as following command line.
```
$ cd ./script
$ docker-compose up
```

#### Create a channel
In order to send a transaction, a channel must be created among the peers. The following command creates a channel with by send `ch1.tx` transaction to orderer. It returns `ch1.block` as genesis block for channel blockchain.
```
$ ./script/create-channel.sh
```

#### Join peers into the channel
After a channel creation, peers need to join the channel. The following command line is an example in order for peer0 to join the channel `ch1`.
```
$ ./script/peer0-join.sh
```

#### Install a chaincode
After all peers joined the channel `ch1`, let's install a chaincode on each peer. Installing a chaincode on peer0 is as follows.
Note: we do not need install the chaincode on all peer nodes. Installing it on peer0 is enough to do instantiation and sending transactions.
The chaincode is a basic chaincode which contains assets `A` and `B` after the initiation.
```
$ ./script/installCCpeer0.sh
```

#### Instantiate the chaincode
The following command line instantitate the chaincode on the channel.
```
$ ./script/instantitateCC.sh
```

#### Query
The following command line will show the amount of the asset `B`.
```
$ ./script/query.sh
```

#### Invoke
The following command line will do a transaction sending `20` from `A` to `B`.
```
$ ./script/invoke.sh
```
