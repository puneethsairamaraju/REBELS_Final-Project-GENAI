# How-to Configure a Discord Bot with OwlMind?

This document explains how to configure a Discord Bot and connect to a OwnMind Agent-based Bot Runner.

You will need:
1. Create a DISCORD TOKEN (Application Key), which represnets your Bot within Discord
2. Generate the URL to attach the Bot to our Server
3. Deploy the Bot to our Discord Server
4. Connect your Bot to an OwlMind Bot Runner


## (1) Create a DISCORD TOKEN 

(Source: [DiscordPy](https://discordpy.readthedocs.io/en/stable/discord.html))

(1.a) Go to Discord Developer Portal and login:

[https://discord.com/developers/docs/intro](https://discord.com/developers/docs/intro)


(1.b) Click on 'Applications' (top-left)

(1.c) In the 'Applications' page, click on 'New Application'

![Application->New Application](/docs/images/discord-1.png)

---


(1.d) Provide a Name and Description; this will show in Discord later, thus e.g enter the name of your Project Group and a Quick Description of your group (name, class code) and project.

> Note:
> Change only Name and Description; dont mess with any other parameters on this page!

(1.e) Click on 'Bots' menu

![Bot Name](/docs/images/discord-2.png)

---

(1.f) Basic bot configuration:

1. Enable PUBLIC BOT
1. Enable MESSAGE CONTENT INTENT
1. Make sure that Require OAuth2 Code Grant IS NOT checked
1. Add an Icon

* Don't worry about the 'Permissions'
* SAVE IT

> [IMPORTANT}
> Without MESSAGE CONTENT INTENT enalbed your Bot will not start!
> It will return an error message like:
>
> raise PrivilegedIntentsRequired(exc.shard_id) from None
> discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled __

![Bot Configuration](/docs/images/discord-3.png)

(1.i) click RESET TOKEN

![Generate TOKEN](/docs/images/discord-6.png)


> NOTE:
> The TOKEN will only show up AFTER you click 'RESET TOKEN'


## (2) Generate the URL to attach the Bot to our Server

Got 'OAuth2':

1. Select 'Bot' from 'OAuth2 URL Generator'
1. Select all entries under 'Text Permissions' (within 'Bot Permissions')
1. Copy the URL from 'Generated URL'

![Bot Configuration](/docs/images/discord-4.png)

![Bot OAuth](/docs/images/discord-7.png)


## (3) Deploy the Bot to our Discord Server

* You must be ADMIN (or have "Manage Server") permission to invite the Bot.
* At this point reach out to the the Teacher, TA or designated Master of Bots:
  * Provide the URL from 'Generated URL' from Step (2)
* After the Bot has been invited into the Server, you should be able to check its presence by typing in the handler e.g. @DemoBot.
* The Bot will be inactive until you complete step (4) and connect this Bot Application to a OwlMind Bot Runner (and execute it).

![Bot Permissions](/docs/images/discord-8.png)


## (4) Connect your Bot to an OwlMind Bot Runner

* You must have a Python 3.10+ enviroment installed.
* The Bot Runner is a blocker process; it will be keeping the bot alive while executing
* If you stop the Bot Runner, the Bot goes offline.
* Due to the nature of the Discord Bot implementation, one cannot execute the Bot Engine from a Jupyter Notebook or similar.

(4.a) Download OwnMind from:

https://github.com/GenILab-FAU/owlmind

(4.b) Configure the 'Getting Started' Bot Runner in ./bot-1.py

* With teh TOKEN from Step (1), EITHER [configure a file .env](https://medium.com/@oadaramola/a-pitfall-i-almost-fell-into-d1d3461b2fb8) OR hard-code TOKEN={Your_Token}
* Install Python requirements from requirements.txt (pip3 insall -r requirements.txt)
* Execute the code 

```
python3 bot-1.py
```
The Bot should go online and able to respond some very basic sentences.



## COMMON PROBLEMS

* Issues with Python3 version compatibility

We tested with Python 3.11, 3.12, and above. 

Check your python version with:

```
$ python3 --version
Python 3.13.1
```



* Missing module **audioop**

This seems to be related to python3.13>. Importing this module has been included in requirements.txt. 

Alternatively:

```
pip3 install audioop-lts
```

## What to do next?

* Configure dialog Rules in bot-1.py to support different Use Cases
* Configure GenAI Pipelines with bot-1.py to extend conversation capabilites
* Configure Prompt Engineering Workflows to improve reasoning.
* Configure Artifacts in the GenAI Pipelines to extend reasoning capabilites










