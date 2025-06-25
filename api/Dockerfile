# api/Dockerfile
FROM python:3.11
COPY api/ /app
COPY src/gridworks_asl/ /app/gridworks_asl
# Deploy API independently

# ui/Dockerfile  
FROM node:18
COPY ui/ /app
# Deploy UI independently