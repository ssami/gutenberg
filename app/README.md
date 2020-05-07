# Purpose

May 2020: 
I wrote this app a while ago to (I think) explore how to set up a model management storage and management system. 

The idea was that Couchbase (why CB? I think I'd learned about it recently and wanted to try it)would serve as the metadata backend and that Minio served as a binary storage solution for the models. 

This Flask application in turn would give you information about the model and also perform model predictions. 

The inference engine was a separate repo called `gbft` (I think). 

I have more/better ideas about stuff I want to build now so I'll save what I have just so it's available and move on. 