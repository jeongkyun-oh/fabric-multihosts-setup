configtxgen -profile TwoOrgsOrdererGenesis -outputBlock genesis.block
mv genesis.block /root/testnet/crypto-config/ordererOrganizations/ordererorg0/orderers/orderer0.ordererorg0/
