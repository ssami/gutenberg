# RESTful service for the WhenText project

A model that makes predictions as to which era of time a text was written. 
Components: 
  + A DB to store the model info, with IDs for each model while binary files themselves live on the local environment
  + A DB to store feedback, indexed by the model ID -- text, original prediction and corrected prediction
  + A local Flask service with well-defined backend to upload models, perform predictions, give human feedback and training
  + A front end for the Flask service

Currently in development: 
+ Redis to store the model info 
+ Minio in Dockerized form with simple temporary store in /data to hold model binary files
+ Local Flask service with simple model info upload and info get

## Get all available models 

*GET /model* 

Response: 
  - 200 with list of all available models, their F1 scores, and which is currently live (that is, being hosted in the machine)
  - 500 if something really goes wrong

## Get all information on a specific model

*GET /model/{modelId} 

Response: 
  - 200 with all information about this model
  - 500 if something really goes wrong


## Upload a model 

*POST /model*

Accept: .bin files only
Response: 
  - 201 if model is correctly uploaded; "Location" header contains the modelId it was created with
  - 500 if upload went wrong (server error)

Takes a .bin file produced by the FastText training framework and stores it in local memory. 

## Make a model live or make it un-live

*PUT /model/{modelId}?live=true*

Response:  
  - 204 if the model status was successfully changed
  - 404 if the model id was not found

## Make a prediction

*POST /prediction*

Request body: 
```
{
	"text": "a long piece of text that can be classified"
}
```
Accept: JSON input format with text

Response: 
  - 200 for a successful prediction
  - 400 if input format is incorrect
  - 404 if model does not exist
  - 500 if something went wrong (server error)

Response body: 
```
{
	"prediction": "1920", 
	"confidence_level": 0.5
}
```

Takes a JSON input with text to be classified. This is a POST request instead of a GET because the body of the input can be arbitrarily long (realistically, let there be a limit of 500 characters). Note also that a POST request is not idempotent, whereas a GET request is expected to be and could be cached. POST makes sense because the model could change in the background. 

This prediction is made with whichever model is currently live. 

## Give feedback for a prediction 

*POST /model/*

Request body: 
```
{
	"text": "some long text which is to be classified", 
	"modelId": 12345, 
	"model_prediction": 1920,
	"actual_prediction": 1950
}
```
Response: 
  - 201 for successful feedback creation
  - 500 if something goes wrong

This endpoint takes in the text which this model tried to predict, the actual prediction and the human suggested prediction, and stores this in the feedback DB. 
