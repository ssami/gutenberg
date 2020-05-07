#!/bin/bash

apt-get update && apt-get install -y curl vim
curl -sL https://deb.nodesource.com/setup_10.x | bash -
apt-get install -y nodejs

npm install -g @angular/cli
