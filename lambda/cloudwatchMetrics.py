import boto3
import json
import requests
from datetime import datetime, timedelta

# AWS Clients
cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
ec2 = boto3.client('ec2', region_name='ap-south-1')

# Notification Settings
USE_SLACK = False  # Set to True if you want Slack notifications
USE_DISCORD = False  # Set to True if you want Discord notifications

# Webhook URLs
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZ"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/XXXXXXXXX/YYYYYYYYYYYYYYYYYYYYY"

# EC2 Tag Settings
TAG_KEY = 'Purpose'
TAG_VALUE = 'test'
DO_NOT_STOP_TAG = 'DoNotStop'
REGION = 'ap-south-1'

# Function to send notifications
def send_notification(message):
    headers = {'Content-Type': 'application/json'}
    
    if USE_SLACK:
        slack_message = {"text": message}
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_message), headers=headers)
    
    if USE_DISCORD:
        discord_message = {"content": message}
        requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(discord_message), headers=headers)

# Function to fetch CloudWatch metrics
def get_metric(instance_id, metric_name, start_time, end_time):
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average']
    )
    datapoints = response.get('Datapoints', [])
    if not datapoints:
        print(f"No data for {metric_name} on {instance_id}. Defaulting to 0.")
        return 0  # Default value when no data is found
    return datapoints[0]["Average"]

# Function to fetch running EC2 instances with the specific tag
def get_running_instances():
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]}
        ]
    )
    instances = []
    for res in response['Reservations']:
        for instance in res['Instances']:
            instance_id = instance['InstanceId']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            instances.append({'InstanceId': instance_id, 'Tags': tags})
    return instances

# Function to fetch instances that should NOT be stopped
def get_do_not_stop_instances():
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': f'tag:{DO_NOT_STOP_TAG}', 'Values': ['True']}
        ]
    )
    return [instance['InstanceId'] for res in response['Reservations'] for instance in res['Instances']]

# Function to stop idle instances
def stop_idle_instances():
    instances = get_running_instances()
    do_not_stop_instances = get_do_not_stop_instances()

    # Define the time range (Last 1 Hour)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    for instance in instances:
        instance_id = instance['InstanceId']

        # Skip instances that have the DoNotStop=True tag
        if instance_id in do_not_stop_instances:
            print(f"Instance {instance_id} has 'DoNotStop' tag. Skipping...")
            continue

        # Fetch metrics
        cpu_util = get_metric(instance_id, 'CPUUtilization', start_time, end_time)
        network_in = get_metric(instance_id, 'NetworkIn', start_time, end_time)
        network_out = get_metric(instance_id, 'NetworkOut', start_time, end_time)
        disk_read = get_metric(instance_id, 'DiskReadOps', start_time, end_time)
        disk_write = get_metric(instance_id, 'DiskWriteOps', start_time, end_time)

        print(f"Instance {instance_id} Metrics:")
        print(f"  CPU: {cpu_util}%")
        print(f"  Network In: {network_in} bytes")
        print(f"  Network Out: {network_out} bytes")
        print(f"  Disk Read Ops: {disk_read}")
        print(f"  Disk Write Ops: {disk_write}")


        # Idle Conditions: Low CPU, Low Network, Low Disk Activity
        if cpu_util < 5 and network_in < 5000 and network_out < 5000 and disk_read < 1 and disk_write < 1:
            print(f"Instance {instance_id} is idle. Stopping it...")

            # Stop the instance
            ec2.stop_instances(InstanceIds=[instance_id])

            # Send Notification
            send_notification(f"EC2 Instance `{instance_id}` was stopped. Reason: Idle for over an hour with low CPU/Network/Disk usage")
        else:
            print(f"Instance {instance_id} is active. Keeping it running.")

# Function to send a warning at 8:50 PM
def send_9pm_warning():
    instances = get_running_instances()
    
    if not instances:
        return  # No instances to warn about

    message = "**Reminder:** The following EC2 instances will be stopped at 9 PM unless they are tagged with `DoNotStop=True`:\n"
    for instance in instances:
        message += f"- `{instance['InstanceId']}`\n"
    
    message += "\nTo keep an instance running, add the tag `DoNotStop=True` before 9 PM."
    send_notification(message)

# Main function
def lambda_handler(event, context):
    current_time = datetime.utcnow()
    
    # Check for manual execution
    if event.get("manual", False):
        print("Manual execution triggered. Stopping idle instances now...")
        stop_idle_instances()
        return

    # Automatic execution based on time
    if current_time.hour == 15 and current_time.minute == 50:  # 8:50 PM IST
        send_9pm_warning()
    
    if current_time.hour == 16 and current_time.minute == 0:  # 9:00 PM IST
        stop_idle_instances()

if __name__ == "__main__":
    event = {"manual": True}  # Simulating a manual trigger
    lambda_handler(event, None)  # Directly calling the Lambda function