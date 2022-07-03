import json
import hashlib
import re
import os
import concurrent.futures
from urllib.parse import urlparse
import requests
import boto3


# Keep tab of global blacklists
GLOBAL_BLACKLIST = set()

# Override AWS Region below, otherwise will use Lambda function's region
try:
    REGION_NAME = os.environ["AWS_REGION"]
except (NameError, KeyError):
    REGION_NAME = "us-west-2"

# Set DynamoDB client and table name
DDB = boto3.client("dynamodb", region_name=REGION_NAME)
TABLENAME = "url-shortner-new"

# Iterate through the list to locate blacklisted domains
URLS = ["https://raw.githubusercontent.com/hectorm/hmirror/master/data/spam404.com/list.txt",
        "https://raw.githubusercontent.com/chadmayfield/pihole-blocklists/master/lists/pi_blocklist_porn_top1m.list",
        "https://www.stopforumspam.com/downloads/toxic_domains_whole.txt"]


def update_blacklist(url):
    """Update global blacklist from the blacklisted domains."""
    try:
        str_lists = requests.get(url).text
        lists = re.split(r"\n", str_lists)
        GLOBAL_BLACKLIST.update(set(lists))
    except requests.exceptions.MissingSchema:
        pass  # skip invalid urls


# Start multithreading on individual urls
with concurrent.futures.ThreadPoolExecutor() as executor:
    _ = [executor.submit(update_blacklist, url) for url in URLS]


def lambda_handler(event, context):
    """Call Lambda's function handler."""
    # /lambda endpoint on API Gateway will keep the function warm
    if event["path"] == "/lambda":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps("Container Warm..")
        }
    # "/" resource on API Gateway is the url shortner domain
    if event["resource"] == "/":
        response = create_url(event)
    else:
        response = get_url(event)

    return response


def create_url(event):
    """Create shortened url from the event."""
    long_url = event["headers"]["url"]
    url_components = urlparse(long_url)
    protocol = url_components.scheme

    # Clean string to remove any whitespace and protocols
    new_str = long_url.strip()
    new_str = new_str.replace(" ", "%20")
    new_str = new_str.replace("https://", "")
    new_str = new_str.replace("http://", "")

    if protocol:
        long_url = f"{protocol}://{new_str}"
    else:
        long_url = f"http://{new_str}"

    # Check if webpage is legit
    url_validity = check_valid_url(long_url)
    print(f"url_validity is {url_validity}")

    if url_validity is not True:
        return {
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(str(url_validity))
        }

    short_url = hashlib.md5(long_url.encode("utf-8")).hexdigest()[:6]

    try:
        DDB.put_item(
            TableName=TABLENAME,
            Item={
                "longUrl": {
                    "S": long_url
                },
                "shortUrl": {
                    "S": short_url
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
        return api_response

    except Exception as exception:
        print(f"Unable to query. Error: {exception}")


def get_url(event):
    """Get original URL from the hashed value."""
    retrieve_url = event["path"]
    retrieve_url = retrieve_url.replace("/", "")

    try:
        response = DDB.query(
            TableName=TABLENAME,
            KeyConditionExpression="#yr = :yyyy",
            ExpressionAttributeNames={
                "#yr": "shortUrl"
            },
            ExpressionAttributeValues={
                ":yyyy": {
                    "S": retrieve_url
                }
            }
        )
        full_url = response["Items"][0]["longUrl"]["S"]
        api_response = {
            "statusCode": 301,
            "headers": {
                "location": full_url
            },
            "body": json.dumps(response)
        }
        return api_response

    # If hash not found, return to home page
    except IndexError:
        return {"statusCode": 301, "headers": {"location": "https://trim.live"}, "body": json.dumps("Invalid webpage")}
    except Exception as exception:
        print(f"Unable to query. Error: {exception}")


def check_valid_url(url):
    """Check for URL Validity before adding to it the database."""
    try:
        current_url = urlparse(url)
        if current_url.hostname in GLOBAL_BLACKLIST:
            raise requests.exceptions.HTTPError(
                "Cannot use this domain, try another URL")
        r = requests.head(url, timeout=1, allow_redirects=True)
        r.raise_for_status()
        status_code = r.status_code
        print(status_code)
        if status_code in (301, 307):
            raise requests.exceptions.HTTPError(
                "Enter a different URL. Redirects aren't allowed")

    except requests.exceptions.Timeout as exception:
        return f"Timeout Error: {exception}"
    except requests.exceptions.HTTPError as exception:
        print(f"HTTP Error: {exception}")
        return exception
    except requests.exceptions.ConnectionError as exception:
        return f"Error Connecting: {exception}"
    except requests.exceptions.RequestException as exception:
        return f"Something went wrong. Error: {exception}"
    return r.status_code == requests.codes.ok
