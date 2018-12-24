import boto3, os, time

regionInstances = {}
regions = [ 'us-west-2', 'ap-northeast-2', 'ap-northeast-1', 'ap-southeast-1', 'ap-south-1' ]
publicIPs = []
privateIPs = []
components = {0: 'peer0', 1: 'peer1', 2: 'peer2', 3: 'peer3', 4: 'orderer0', 5: 'kafka-zookeeper', 6: 'client'}

if "AWS_IMAGE_ID" in os.environ :
    imageId = os.environ["AWS_IMAGE_ID"]
if "AWS_INSTANCE_TYPE" in os.environ :
    instanceType = os.environ["AWS_INSTANCE_TYPE"]
if "AWS_KEY_NAME" in os.environ :
    keyName = os.environ["AWS_KEY_NAME"]
if "AWS_KEY_PATH" in os.environ :
    keypath = os.environ["AWS_KEY_PATH"]
if "AWS_SECURITY_GROUP" in os.environ :
    securityGroups = [os.environ["AWS_SECURITY_GROUP"]]
if "AWS_FABRIC_IMAGE_NAME" in os.environ :
    fabricImageName = os.environ["AWS_FABRIC_IMAGE_NAME"]
if "PWD" in os.environ :
    currentPath = os.environ["PWD"]

def create_ami(tagname):
    filters = [
			{
				'Name': 'tag-value',
				'Values': [
					tagname,
					]
				},
			{
				'Name': 'instance-state-name',
				'Values': [
					'running'
					]
				}
			]
    instances = boto3.resource('ec2').instances.filter(Filters=filters)
    id = ""
    for instance in instances:
        id = instance.instance_id
    response = boto3.client('ec2').create_image(
        InstanceId=id,
        Name=fabricImageName,
        Description="Hyperledger fabric initial image in order to setup a sample network"
    )
    f = open("fabric_instance_id.txt", "w")
    f.write(response['ImageId'])
    f.close()

def initiate_fabric_network():
    dest = get_destination(publicIPs[0])
    scp("init_fabric.sh", "%s:~/" % dest)
    ssh(dest, "sudo ./init_fabric.sh")

def initiate_fabric_instance():
    dest = get_destination(publicIPs[0])
    scp("prepare_fabric.sh", "%s:~/" % dest)
    ssh(dest, "sudo ./prepare_fabric.sh")
    scp("-r script", "%s:~/" % dest)
    ssh(dest, "sudo mv ./script /root/testnet/script")

def login(tagname, id):
    f = open("hosts", "r")
    f.readline()
    hosts = []
    for i in range(7):
        line = f.readline()
        hosts.append(line.split()[0])
    f.close()
    os.system("ssh -i %s %s" % (keypath, get_destination(hosts[int(id)])))

def upload_hosts(tagname):
    f = open("hosts", "r")
    f.readline()
    hosts = []
    for i in range(7):
        line = f.readline()
        hosts.append(line.split()[0])
    f.close()
    source = currentPath + '/private'
    print(source)
    commandline = "sudo mv ~/private /etc/hosts"
    for i in range(7):
        print(get_destination(hosts[i]))
        scp(source, "%s:~/" % get_destination(hosts[i]))
        ssh(get_destination(hosts[i]), commandline)

def get_destination(address):
    return "ubuntu@%s" % address

def ssh(address, commandline):
    os.system("ssh -i %s %s \"%s\"" % (keypath, address, commandline))

def scp(source, destination):
    os.system("scp -i %s %s %s" % (keypath, source, destination))

def write_hosts_file(tagname):
    hosts = get_hosts(tagname)
    f = open("hosts", "w")
    f.write("127.0.0.1 localhost\n")
    for i in range(7):
        f.write("%s %s\n" % (hosts[0][i], components[i]))
    f.close()
    f = open("private", "w")
    f.write("127.0.0.1 localhost\n")
    for i in range(7):
        f.write("%s %s\n" % (hosts[1][i], components[i]))
    f.close()

def	get_hosts(tagname):
	hosts = []
	for i in range (0, len(regions)):
		ec2 = boto3.client('ec2', region_name = regions[i])
		response = ec2.describe_instances(
			Filters = [
				{
					'Name': 'tag-value',
					'Values': [
						tagname,
					]
				},
			],
		)

		ids = []
		for reservation in response["Reservations"]:
			for instance in reservation["Instances"]:
				ids.append (instance["InstanceId"])
				for interface in instance["NetworkInterfaces"]:
					privateIPs.append (interface["PrivateIpAddress"])
					publicIPs.append (instance["PublicIpAddress"])
		regionInstances[regions[i]] = ids

	public, private = publicIPs, privateIPs
	print("Public IPs: %s" % publicIPs)
	print("Private IPs: %s" % privateIPs)
	# print(hosts)
	# env.hosts = hosts
	return [public, private]

def create_instance_with_fabric_image(num, name):
    f = open("fabric_instance_id.txt", "r")
    id = f.read()
    create_instance(num, name, id)

def create_instance(num, name, id=imageId):
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances (
    ImageId = id,
    InstanceType= instanceType,
    MinCount=1,
    MaxCount=int(num),
    KeyName=keyName,
    Monitoring={
        'Enabled': False,
        },
        SecurityGroups=['default'],
        TagSpecifications=[
        {
        'ResourceType': 'instance',
        'Tags':[
            {
            'Key': 'type',
            'Value': name,
            }
            ]
        }
        ]
    )
    print instance

def terminate_instances(tagname):
	filters = [
			{
				'Name': 'tag-value',
				'Values': [
					tagname,
					]
				},
			{
				'Name': 'instance-state-name',
				'Values': [
					'pending',
					'running',
					'stopping',
					'stopped'
					]
				}
			]
	boto3.resource('ec2').instances.filter(Filters=filters).terminate()
