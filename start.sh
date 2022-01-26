#!/bin/sh 

docker build -t epam . 
docker run --name epam -it -p 3000:3000 epam