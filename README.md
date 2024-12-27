# Deadpool Application

# Overview 
The Deadpool application facilities a draft-like process for an annual Celebrity Deathpool, not unlike a fantasy football draft.  The objective, of course, is to pick the most celebrities who will pass away throughout the year.  

## Motivation
Historically, we tracked this on a spreadsheet; however, with the increase in the number of participants (14 this year) and the number of picks to 20 per person, or 280 today picks.  

To facilitate the volume of picks, we needed some software automation.  As an experiment, I wrote this all utilizing Data engineering and Data science principles and techniques vs. traditional software engineering techniques.  While this could have been done with less overall cost by utilizing SWE practices, it was a great exercise to continue to learn about the ecosystem.  

## Features
The following features are part of this overall application.

* Responsive web and mobile application
* User authentication
* Cloud-hosted data for high availability
* Round-robin drafting process (players go in a particular order and cycle through until complete.)
* SMS-based notification of drafts and deaths via [Twillio](https://www.twilio.com).
* Automatic population of ages and birth dates and validates Wikipedia ID (for death checking.)
* Daily automation that checks for celebrity deaths.
* Slack notification for maintenance issues for the primary moderators.
* LaunchDarkly feature flagging for new features.
* Mixpanel for user analytics.
* Searchable database of 26k plus living and dead famous people, including information about their deaths and health scraped from Wikipedia.
* XGBoost-based binary classifier for predicting death based on known health issues. 


## Sofware
The entire application sits in four GitHub repos.  
* Streamlit App: (This repo)
* [Prefect Orchestration](https://github.com/broepke/prefect-dka)
* [The Arbiter, LLM Chatbot](https://github.com/broepke/deadpool-llm)
* [Deadpool Analysis and Predictive Model](https://github.com/broepke/deadpool-analysis)

## Architechture
The architecture comprises many common Data Analytics, Data Science, and Data Engineering tools.  All modern practices were followed while constructing this application.
![The Deadpool Architecture](dp_arch.png)

## Virtual Machine Deployment on EC2

**NOTE**: *This is the original deployment method.  It has been replaced by a container-based deployment.*

The application is hosted on AWS using:

* Launch Template: With extensive user-data script (in this repo) for deploying and configuring the server and services.
* AutoScaling Group: Setup to help with deploy, refresh and scaling.
* Load Balancer: With the ASG, but additionally so it can be hosted behind a custom secure domain.
* HTTP: Via Route53 through the load balancer.  Hosted on dataknowsall.com domain.
* GitHub WebHooks: The ability for a change to the main branch in the repo to trigger new code to be deployed.


Check the service status

```bash
sudo systemctl status streamlit-agent
sudo systemctl status github-webhook
```

## Container Based Deployment

### Docker

```bash
docker build --no-cache -t deadpoolapp:latest .


docker run -p 8501:8501 deadpoolapp
```

### ECR

To build the container and publish to ECR, Follow the steps in the app's **Push commands for deadpool-docker-private** settings.  Simple as that.

### ECS

To add the **second Target Group**, we need to [Registering multiple target groups with a service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/register-multiple-targetgroups.html) via the **AWS CLI**. First Export the **Service Description** to JSON so you can see where to add a new **Target Groups** and copy the structure of the other one.

```bash
aws ecs describe-services \
    --services deadpool-fargate-service \
    --cluster deadpool-app-fargate \
    --query "services[0]" \
    > deadpool-fargate-service.json

```

And finally **Update** the service

```bash
aws ecs update-service \
    --cluster deadpool-app-fargate \
    --service deadpool-fargate-service \
    --load-balancers \
    targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:############:targetgroup/deadpool-fargate-tg/3ba657d612a4194e,containerName=deadpool,containerPort=8501 \
    targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:############:targetgroup/deadpool-fargate-tg-flask/84f8864279670ad9,containerName=deadpool,containerPort=5000
```

## CI/CD

### GitHub WebHooks for Automatic Repo Updates


### GitHub Actions for CI/CD

The architecture needs to be the same with your image's build environment.


## References
**AWS EC2 Setup**: 
 [How to Deploy a Streamlit App using an Amazon Free ec2 instance?](https://towardsdatascience.com/how-to-deploy-a-streamlit-app-using-an-amazon-free-ec2-instance-416a41f69dc3)

**AWS ECS**: [How to Setup AWS ECS Fargate with a Load Balancer | Step by Step](https://www.youtube.com/watch?v=o7s-eigrMAI)

**Snowflake**: [Connect Streamlit to Snowflake](https://docs.streamlit.io/knowledge-base/tutorials/databases/snowflake)

**Docker and Streamlit**: [Deploy Streamlit using Docker](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
