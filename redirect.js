var AWS = require("aws-sdk");

exports.handler = (event, context, callback) => {

  //context.done(null, "This message header was processed by Amazon " +event.headers["header1"]);


AWS.config.update({
  region: "us-west-2"
});

//console.log(event)
var getUrl =  event.path;
getUrl = getUrl.replace('/','');
console.log(getUrl);

var docClient = new AWS.DynamoDB.DocumentClient()

var params = {
    TableName : "url-shortner-new",
    KeyConditionExpression: "#yr = :yyyy",
    ExpressionAttributeNames:{
        "#yr": "shortUrl"
    },
    ExpressionAttributeValues: {
        //":yyyy": event.url
        ":yyyy": getUrl
        
    }
};

docClient.query(params, function(err, data) {
    if (err) {
        console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
    } else {
        console.log("Data Items is")
        console.log(data)
        var fullUrl = data['Items'][0]['longUrl'];
        //var method = data['Items'][0]['method'];
        //console.log(method);
        var location = fullUrl;
        console.log("Location is "+location);
         var result = {
        "statusCode": 301,
        "headers": {
            "location": location
            },
            "body": JSON.stringify(data)
            };
            callback(null, result);
           
       
        
    }//end else
});


}

