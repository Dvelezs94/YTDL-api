#!/bin/bash

eval `ssh-agent -s`
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 696716568292.dkr.ecr.us-east-1.amazonaws.com^
ssh-add ~/.ssh/github.pem
docker build -t y2dl .
docker tag y2dl:latest 696716568292.dkr.ecr.us-east-1.amazonaws.com/y2dl:latest
docker push 696716568292.dkr.ecr.us-east-1.amazonaws.com/y2dl:latest
docker ps | grep "y2dl:latest" | cut -d" " -f1 | xargs docker stop
