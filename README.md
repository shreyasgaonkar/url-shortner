# [trim.live](https://trim.live/)

https://trim.live provides free and fast url shortner that will work forever. We don't clear the results and you can keep using the same url to fetch the original websites.

Uses ```AWS API Gateway, Lambda and DynamoDB``` under the hood. Use ```url-shortner-combined.js``` or ```url-shortner-combined.py``` as a single function to create and retrieve urls from the hash stored off DynamoDB.

To prevent spammers, we make a HEAD request using the [requests module](https://github.com/shreyasgaonkar/aws-lambda-code-samples/tree/master/lambda-layer) using Lambda layer to check if the URL is valid before added it to the database.

#### Minor update:
Since [url-shortner-combined.js](url-shortner-combined.js) was created with Node8.X is past EOL, use [url-shortner-combined.py](url-shortner-combined.py) built on Python3.6 for extended EOL.

```console
$ aws dynamodb describe-table --table-name url-shortner --output table
```
```
--------------------------------------------------------------------------+
|                             DescribeTable                               |
+-------------------------------------------------------------------------+
||                                Table                                  ||
||+----------------------------------+----------------------------------+||
|||                         AttributeDefinitions                        |||
||+----------------------------------+----------------------------------+||
|||          AttributeName           |          AttributeType           |||
||+----------------------------------+----------------------------------+||
|||             shortUrl             |                S                 |||
||+----------------------------------+----------------------------------+||
|||                              KeySchema                              |||
||+----------------------------------+----------------------------------+||
|||             shortUrl             |              HASH                |||
||+----------------------------------+----------------------------------+||
```
