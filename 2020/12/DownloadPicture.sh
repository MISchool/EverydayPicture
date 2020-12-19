#!/bin/bash
cd /www/wwwroot/EverydayPicture

mkdir -p `date +%Y`/`date +%m` 
#cd `date +%Y`/`date +%m` 
wget -c 'https://api.ixiaowai.cn/api/api.php?18' -O /www/wwwroot/EverydayPicture/`date +%Y`/`date +%m`/`date +%Y%m%d%M%N`.jpg --content-on-error --no-check-certificate

#date +"%Y-%m-%d-%T" >> record.txt
#git add .; git commit -m `date +%Y-%m-%d-%T`
