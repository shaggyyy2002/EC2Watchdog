## Overview
This week was focused on setting up an AWS Lambda function for automating EC2 instance management. The Lambda function checks CloudWatch metrics to identify idle instances and stops them unless they are tagged with DoNotStop=True. Notifications are sent via Slack or Discord.

## Configuring and using a role

When you run commands using a profile that specifies an IAM role, the AWS CLI uses the source profile's credentials to call AWS Security Token Service (AWS STS) and request temporary credentials for the specified role

To ensure the EC2 Watchdog Lambda functions correctly, attach the AWS-managed IAM policies to the execution role
- This project requires IAM roles with permissions to manage EC2 instances, SNS notifications, and CloudWatch monitoring.

### PRO TIP: Never add Secrets in `.env` file even if it contains `.gitignore`

#### Configuration and credential file settings in the AWS CLI

The config and credentials files are organized into sections. Sections include profiles, sso-sessions, and services. A section is a named collection of settings, and continues until another section definition line is encountered. Multiple profiles and sections can be stored in the `config` and `credentials` files.

1. `aws configure --profile <NameofProject>` : it will create or update the following file. 
`~/.aws/credentials`.  `P.S: ` Never add it in the root repo keep it your local setup. Never push it to Github Directory. 
2. Once used the command it will ask you credentials: 
    - AWS Access Key ID [None]: <`access-key-id`>
    - AWS Secret Access Key [None]:  <`secret-access-key`>
    - Default region name [None]: <`default-region`>
    - Default output format [None]: `json`
3. You can check them using: 
    - `cat ~/.aws/credentials`
    - `cat ~/.aws/config`

## Set and view configuration settings using commands

There are several ways to view and set your configuration settings using commands.

```
aws configure
```

Run this command to quickly set and view your credentials, Region, and output format. The following example shows sample values.

```
$ aws configure
```
Output: 
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
```

```
$ aws configure set
```
You can set any credentials or configuration settings using aws configure set. Specify the profile that you want to view or modify with the `--profile` setting.

For example, the following command sets the region in the profile named integ.

```
$ aws configure set region us-west-2 --profile integ
```

To remove a setting, manually delete the setting in your config and credentials files in a text editor.

```
$ aws configure get
```
You can retrieve any credentials or configuration settings you've set using aws configure get. Specify the profile that you want to view or modify with the --profile setting.

For example, the following command retrieves the region setting in the profile named integ.

```
$ aws configure get region --profile integ
us-west-2
```

If the output is empty, the setting is not explicitly set and uses the default value.

```
aws configure import
```
Import CSV credentials generated from the IAM web console. This is not for credentials generated from IAM Identity Center; customers who use IAM Identity Center should use aws configure sso. A CSV file is imported with the profile name matching the username. The CSV file must contain the following headers.

Output: 
```
User Name

Access key ID

Secret access key
``` 

Note: 
During initial key pair creation, once you close the Download .csv file dialog box, you cannot access your secret access key after you close the dialog box. If you need a .csv file, you'll need to create one yourself with the required headers and your stored key pair information. If you do not have access to your key pair information, you need to create a new key pair.

```
$ aws configure import --csv file://credentials.csv
```

### Testing AWS CLI & Boto3 Access to EC2

1. Check if AWS CLI can list all EC2 instances on your account. You can speciy region by using --region <`region`>: <br>
 Run the following command:
    ```
    $ aws ec2 describe-instances --profile <$namedAWSCLIprofile>
    ```
    Output: 
    ```
        "Reservations": [
        {
            "ReservationId": "r-**-0bc432a8de5",
            "OwnerId": "74***51",
            "Groups": [],
            "Instances": [
                {
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            ...
                        }
                    ]
                }
            ]
    ```

2. Verify IAM Role Permissions: 
    ```
    $ aws sts get-caller-identity --profile <$namedAWSCLIprofile>
    ```
    Output: 
    ```
    {
    "UserId": "AIDA**CD6",
    "Account": "746*****4951",
    "Arn": "arn:aws:iam::74***4951:user/EC2Stopper"
    }   
    ```

### Pre-requisites Before Writing Lambda:

1. [X] Verify AWS CLI & Boto3 Access: 
    - Run aws ec2 describe-instances and confirm it returns valid data. 
    - Try fetching EC2 details using Boto3 in a Python script.
2. [X] Define IAM Role for Lambda: 
    - Does the Lambda function have enough permissions? 
    - Attach necessary policies (EC2, SNS, CloudWatch, EventBridge).
3. [X] Decide Input & Output for Lambda:  
    - What will trigger it? (EventBridge rule at 9 AM & 9 PM)
    - What data will it receive? (List of instances + tags)
    - What should it return? (Success/failure logs + notifications)
4. [X] Set Up Logging
   - Will it log to CloudWatch?
   - Do we need alerts on failures?

5. [X] Define the Logic Flow
    - Fetch all EC2 instances.
    - Filter by tags (Test, Dev, etc.).
    - Check if the instance is idle (CPU, Network, Disk).
    - If idle, stop the instance. Log the action and notify Slack.


# AWS Lambda Learning 

## 📌 Phase 1: Understanding the Basics
Before writing Lambda functions, you need to understand:
   - [What is AWS Lambda?](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) (Serverless computing, event-driven execution) 
   - How does AWS Lambda work? (Triggers, execution model, scaling)  
     - A Lambda function is a piece of code that runs in response to events, such as a user clicking a button on a website or a file being uploaded to an Amazon Simple Storage Service (Amazon S3) bucket.
   - [AWS IAM Roles for Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html#permissions-executionrole-api) (Permissions, security policies)
   - [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/) (Free tier, cost optimization)
   - [Deployment Methods](https://www.serverlessguru.com/blog/terraform-create-and-deploy-aws-lambda) (Console, AWS CLI, Terraform, AWS CDK, Serverless Framework)

## 📌 Phase 2: Writing Your First AWS Lambda Function
- Hello World in Lambda (Just print "Hello from Lambda!")
    ```py
    import json

    # entry point of lambda
    # want to print in CLI pass (none,none)
    def lambda_handler(event, context): 
        print("Hello from Lambda") #logs in cloudwatch
        return{
            "statusCode" : 200,
            "body" : json.dumps({"message" : "Hello World"})
        }
    # If running locally, you can test it with:    
    respone = lambda_handler(none, none)
    print(response) # This will print the JSON output       
    ```
    `Output:`
    ```json
        Hello from Lambda
        {
            'statusCode': 200, 
            'body': '{"message": "Hello World"}'
        }
    ```

- [Using Boto3 in Lambda Connecting to AWS services](https://docs.aws.amazon.com/code-library/latest/ug/python_3_lambda_code_examples.html)
- Fetching EC2, S3, DynamoDB data (Basic API calls using boto3) `[~/Ec2WatchDog/lambda/connect.py]`
- [Logging with CloudWatch](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html) (Viewing logs for debugging)

- [X] Project Idea: Write a Lambda function to list S3 buckets and log the names. (~/Ec2WatchDog/lambda/checkS3.py)

## 📌 Phase 3: AWS Lambda Triggers & Event Handling
- [How AWS Lambda Gets Triggered](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html) (S3, SNS, SQS, API Gateway, EventBridge) 
- Event-Driven Lambda (Understanding event payloads & responses)
- Writing a Lambda function triggered by an S3 file upload
- Processing SQS Messages with Lambda
- Using API Gateway to expose Lambda as an API

- [ ] Project Idea: Create a Lambda function that sends an email via SES whenever a new file is uploaded to S3.

## 📌 Phase 4: Handling Data in Lambda
- Environment Variables in Lambda
- Reading/Writing Data to S3 from Lambda
- Interacting with DynamoDB (NoSQL DB) using Lambda
- Fetching & processing API data in Lambda

- [ ] Project Idea: Write a Lambda function that retrieves weather data from an API and stores it in DynamoDB.

## 📌 Phase 5: Advanced AWS Lambda Concepts
- Asynchronous Execution & Retry Logic
- Parallel Processing with AWS Step Functions
- Deploying Lambda with Terraform, AWS SAM, Serverless Framework
- Optimizing Lambda Execution Time & Cost
- Cold Start Issues & How to Reduce Them

- [ ] Project Idea: Build a serverless API that handles image processing (resize, watermark) using Lambda & S3.

## 📌 Phase 6: Real-World Use Cases & Best Practices
- Security Best Practices (IAM permissions, VPC, logging)
- Monitoring & Debugging Lambda with X-Ray
- Using AWS Lambda in DevOps (CI/CD, Automation, Infrastructure Monitoring)
- Building Event-Driven Applications with Lambda

- [ ] Project Idea: Automate EC2 cost optimization by stopping unused instances using Lambda & EventBridge.

# AWS CloudWatchMetrics implementation

## Package & region Setup 
Import package [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#using-boto3), [json](https://docs.python.org/3/library/json.html), [requests](https://pypi.org/project/requests/), [datetime](https://docs.python.org/3/library/datetime.html), [timedelta]()

```
import boto3
import json
import requests
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
ec2 = boto3.client('ec2', region_name='ap-south-1')
```

## Notificaion using Slack or Discord (add url. rn webhook not created)

We can use Slack or DIscord webhoook to send in notification to desired channel
```
USE_SLACK = False  # Enable Slack notifications if needed
USE_DISCORD = False  # Enable Discord notifications if needed

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZ"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/XXXXXXXXX/YYYYYYYYYYYYYYYYYYYYY"
```

## Fetching Running Instances

From the previous task we did the same. this function will try to get all the running instances from our AWS account.
```
def get_running_instances():
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Purpose', 'Values': ['test']}
        ]
    )
    instances = [instance['InstanceId'] for res in response['Reservations'] for instance in res['Instances']]
    return instances
```

## Stopping Idle Instances
As project says we need a logic to find out the idle instances which are not runninng anything and need to be shutdown, added a manual feature at the end, but every night at 9PM our function will get trigger and shutdown every ec2 isntance which is ideal with the tag `'purpose' : 'test'` && if any ec2 insrance is tagged -DonotStop it will skip even if idle for the night.

```
def stop_idle_instances():
    instances = get_running_instances()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    for instance_id in instances:
        cpu_util = get_metric(instance_id, 'CPUUtilization', start_time, end_time)
        if cpu_util < 5:
            ec2.stop_instances(InstanceIds=[instance_id])
            print(f"Stopped instance: {instance_id}")
```

## Idle Instance Logic 

To figure out which instance is Idle we can use <br>
    { 
    if <br>
    - `cpu_util < 5` , <br>
    - `network_in < 5000` , <br>
    - `network_out < 5000`,<br>
    - `disk_read < 1`,<br>
    - `disk_write < 1`.<br>
    } <br>

```
        # Idle Conditions: Low CPU, Low Network, Low Disk Activity
        if cpu_util < 5 and network_in < 5000 and network_out < 5000 and disk_read < 1 and disk_write < 1:
            print(f"Instance {instance_id} is idle. Stopping it...")

            # Stop the instance
            ec2.stop_instances(InstanceIds=[instance_id])

            # Send Notification
            send_notification(f"EC2 Instance `{instance_id}` was stopped. Reason: Idle for over an hour with low CPU/Network/Disk usage")
        else:
            print(f"Instance {instance_id} is active. Keeping it running.")
```
once done it will stop the Ec2 instances




# References / Links to Articles

1. [AWS CLI Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. [CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
3. [IAM Role Setup](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-role.html)
4. [Configuration and credential file settings](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)