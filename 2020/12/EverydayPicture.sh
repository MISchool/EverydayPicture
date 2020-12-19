#!/bin/bash
cd /www/wwwroot/EverydayPicture
date +"%Y-%m-%d-%T" >> record.txt
git fetch --all
git pull
git add .; git commit -m `date +%Y-%m-%d-%T`
git push -u origin main
