import json
import hashlib
import boto3

DDB = boto3.client('dynamodb', region_name='us-west-2')
TABLENAME = 'url-shortner-new'


def lambda_handler(event, context):
    """ Main Lambda function """
    if event['resource'] == "/":
        response = create_url(event)
    else:
        response = get_url(event)

    return response


def create_url(event):
    """ Function to create hash for URL shortner """

    long_url = event['headers']['url']

    # Clean string to remove any whitespace and protocols
    new_str = long_url.strip()
    new_str = new_str.replace(' ', '%20')
    new_str = new_str.replace('https://', '')
    new_str = new_str.replace('http://', '')

    # Since we don't know if the website entered is to be served on
    # HTTP or HTTPs, send it to HTTP and let server redirect to HTTPS

    long_url = f"http://{new_str}"
    short_url = hashlib.md5(long_url.encode('utf-8')).hexdigest()[:6]

    try:
        DDB.put_item(
            TableName=TABLENAME,
            Item={
                "longUrl": {
                    'S': long_url
                },
                "shortUrl": {
                    'S': short_url
                }
            },
            ReturnConsumedCapacity="TOTAL",

        )

        # Send data back to API
        url = f"https://trim.live/{short_url}"
        api_response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(url)
        }
        print(api_response)
        return api_response

    except Exception as exception:
        print(f"Unable to query. Error: {exception}")


def get_url(event):
    """ Get original URL from the hashed value """
    retrieve_url = event['path']
    retrieve_url = retrieve_url.replace('/', '')
    print(retrieve_url)

    try:
        response = DDB.query(
            TableName=TABLENAME,
            KeyConditionExpression="#yr = :yyyy",
            ExpressionAttributeNames={
                "#yr": "shortUrl"
            },
            ExpressionAttributeValues={
                ':yyyy': {
                    'S': retrieve_url
                }
            }
        )
        print(response)
        full_url = response['Items'][0]['longUrl']['S']
        api_response = {
            "statusCode": 301,
            "headers": {
                "location": full_url
            },
            "body": json.dumps(response)
        }
        print(api_response)
        return api_response

    except Exception as exception:
        print(f"Unable to query. Error: {exception}")
