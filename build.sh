#!/bin/bash
echo 开始构建...

pftc=`docker ps -a | grep pftc`

if [[ -n $pftc ]];then
  echo $pftc
  docker stop pftc
  docker rm pftc
fi


pfti=`docker images | grep pft`

if [[ -n $pfti ]];then
  echo $pfti
  docker rmi pft:1.0
fi

docker build -t pft:1.0 .
docker run -d --name pftc -v /logs:/logs -p 8888:8888 pft:1.0