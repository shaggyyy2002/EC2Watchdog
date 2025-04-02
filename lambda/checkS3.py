import boto3
    # Write a Lambda function to list S3 buckets and log the names.

def listS3buckets(): 
    s3buckets = boto3.client('s3')
    response = s3buckets.list_buckets()

    #Output buckets names
    print('Existing Buckets')
    for bucket in response['Buckets']:
        print(f'{bucket["Name"]}') 

def lambda_handler(event , context): 
    listS3buckets() 
    return {
        "statusCode" : 200,
        "body" : "Bucket list printed to logs"
    }