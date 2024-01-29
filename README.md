# Deadpool Application

# Overview 
The Deadpool application facilities a draft like process for an annual Celebrity Deathpool, not unlike a fantasy foodball draft.  The objective, of course, is to pick the most amount of celebrities that will pass away throughout the year.  

## Motivation
Historically we simply tracked this on a spreadsheet, however, with the increase in number of participants (14 this year), and the 

In order to facilitate the volume of picks we needed some software automation. As an experiment I wrote this all utilizing Data Engineer, and Data Sciece like principles and technqiues, vs. traditional software engineering techniques.  While this could have been done with less overall cost utilizing SWE practicies, it was a great exercies to continue to learn the ecosystem.  

## Features
The following features are part of this overall application.

* Responsive web and mobile application
* User authentication
* Cloud hosted data for high availability
* Round robin drafting process (players go in a particular order and cycle through until complete.)
* SMS based notification of drafts and deaths via [Twillio](https://www.twilio.com).
* Automatic population of ages and brith dates as well as validates Wikipedia ID (for death checking.)
* Daily automation that checks for celebrity deaths.
* Slack notification for maintenance issues for the primary moderators.
* AWS based Auto-Scale group for workflow execution on EC2 servers.
* 


## Sofware
The entire application sits in four GitHub repos.  
* Streamlit App: (This repo)
* [Prefect Orchestration](https://github.com/broepke/prefect-dka)
* [The Arbiter, LLM Chatbot](https://github.com/broepke/deadpool-llm)
* [Deadpool Analysis and Predictive Model](https://github.com/broepke/deadpool-analysis)

## Architechture
The architecture consists of many common tools for Data Analytics, Data Science and Data Engineering.  All modern practices were followed while constructing this application.
![The Deadpool Architecture](dp_arch.png)


## References
**AWS Setup**: 
 [How to Deploy a Streamlit App using an Amazon Free ec2 instance?](https://towardsdatascience.com/how-to-deploy-a-streamlit-app-using-an-amazon-free-ec2-instance-416a41f69dc3)

**Snowflake**: 
[Connect Streamlit to Snowflake](https://docs.streamlit.io/knowledge-base/tutorials/databases/snowflake)