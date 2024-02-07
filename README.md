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
* AWS-based Auto-Scale group for workflow execution on EC2 servers.
* Searchable database of 26k plus living and dead famous people, including information about their deaths and health scraped from Wikipedia.
* XGBoose-based binary classifier for predicting death based on known health issues. 


## Sofware
The entire application sits in four GitHub repos.  
* Streamlit App: (This repo)
* [Prefect Orchestration](https://github.com/broepke/prefect-dka)
* [The Arbiter, LLM Chatbot](https://github.com/broepke/deadpool-llm)
* [Deadpool Analysis and Predictive Model](https://github.com/broepke/deadpool-analysis)

## Architechture
The architecture comprises many common Data Analytics, Data Science, and Data Engineering tools.  All modern practices were followed while constructing this application.
![The Deadpool Architecture](dp_arch.png)

## EC2

Check the service status

```
sudo systemctl status streamlit-agent
sudo systemctl status github-webhook
```

## References
**AWS Setup**: 
_Note: This is not currently being used.  The application is deployed on Streamlit.app cloud_
 [How to Deploy a Streamlit App using an Amazon Free ec2 instance?](https://towardsdatascience.com/how-to-deploy-a-streamlit-app-using-an-amazon-free-ec2-instance-416a41f69dc3)

**Snowflake**: 
[Connect Streamlit to Snowflake](https://docs.streamlit.io/knowledge-base/tutorials/databases/snowflake)
