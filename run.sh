#!/bin/sh

docker stop lc-zh-ds
docker rm lc-zh-ds
docker build -t lc-zh-ds-img:latest --target streamlit .
docker run --env-file .env --restart unless-stopped -p 8501:8501 --name lc-zh-ds -d lc-zh-ds-img
