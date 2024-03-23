aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 222975130657.dkr.ecr.us-east-1.amazonaws.com

docker build -t deadpool-docker-private .

docker tag deadpool-docker-private:latest 222975130657.dkr.ecr.us-east-1.amazonaws.com/deadpool-docker-private:latest

docker push 222975130657.dkr.ecr.us-east-1.amazonaws.com/deadpool-docker-private:latest