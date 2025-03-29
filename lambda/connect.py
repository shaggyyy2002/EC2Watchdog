import boto3

# Using Boto3 in Lambda Connecting to AWS services
def listallrunninginstances(): 
    ec2Client = boto3.client('ec2')

    # Fetch only running instances
    response = ec2Client.describe_instances(
        Filters = [{'Name' : 'instance-state-name' , 'Values' : ['running']}]
    )

    # Stores Instaces
    instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']: 
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

        instances.append({
            "InstanceID" : instance_id,
            "State" : state,
            "Tags" : tags
        })        

    return instances

if __name__ == "__main__": 
    runninInstances = listallrunninginstances()

    if runninInstances: 
        print("Running EC2 Instances are: ") 
        for instance in runninInstances: 
            print(f"InstancesId : {instance['Instance Id']} , Tags: {instance['Tags']}")
    else: 
        print("NO running Instance")