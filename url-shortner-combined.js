var AWS = require('aws-sdk');
var crypto = require('crypto');
var ddb = new AWS.DynamoDB({
    region: 'us-west-2'
});


exports.handler = (event, context, callback) => {

    if (event.resource == "/") {
        createURL();
    } else {
        getURL();
    }

    /* Functions to create and retrieve the short url */

    function getURL() {
        // Function to get full URL from the hashed value
        console.log(event);
        var getUrl = event.path;
        getUrl = getUrl.replace('/', '');
        console.log(getUrl);

        AWS.config.update({
            region: "us-west-2"
        });

        var docClient = new AWS.DynamoDB.DocumentClient();

        var params = {
            TableName: "url-shortner-new",
            KeyConditionExpression: "#yr = :yyyy",
            ExpressionAttributeNames: {
                "#yr": "shortUrl"
            },
            ExpressionAttributeValues: {
                ":yyyy": getUrl

            }
        };

        docClient.query(params, function(err, data) {
            if (err) {
                console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
            } else {
                console.log("Data Items is");
                console.log(data);
                var fullUrl = data['Items'][0]['longUrl'];
                var location = fullUrl;
                console.log("Location is " + location);
                var result = {
                    "statusCode": 301,
                    "headers": {
                        "location": location
                    },
                    "body": JSON.stringify(data)
                };
                callback(null, result);

            } //end else
        });

    }

    function createURL() {
        // Function to create hash for URL shortner

        var apiResponse = {};
        var longUrl = event.headers.url;
        console.log(longUrl);
        var str = longUrl;
        var newstr = str.replace(/ /g, '').trim();
        newstr = newstr.split(' ').join('%20');
        newstr = newstr.split('https://').join('');
        newstr = newstr.split('http://').join('');
        longUrl = 'http://' + newstr;
        var shortUrl = crypto.createHash('md5').update(longUrl).digest('hex').substring(0, 6);

        var params = {
            Item: {
                "longUrl": {
                    S: longUrl
                },
                "shortUrl": {
                    S: shortUrl
                }
            },
            ReturnConsumedCapacity: "TOTAL",
            TableName: "url-shortner-new"
        };

        var request = ddb.putItem(params);

        request.
        on('success', function(response) {
            var sentUrl = "https://trim.live/" + shortUrl;
            var apiResponse = {
                statusCode: 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                body: JSON.stringify(sentUrl)
            };
            console.log(apiResponse);
            callback(null, apiResponse);
        }).
        on('error', function(response) {

            apiResponse = {
                statusCode: 500,
                headers: {},
                body: "There was an error processing your request " + JSON.stringify(response.data)
            };
            callback(null, apiResponse);

        }).
        send();
    }
};