# discourse_link_checker
A program to find broken links in Discourse

## Overview
The Discourse Link Checker is a tool to automatically validate links on Discourse posts. Specifically, it looks at each link in every post by an admin user. It will not find links that don’t begin with “http(s)://” (but Discourse automatically appends "http://" to outside links, so this script should find all missing links).


## Creating a Discourse Backup
The first step in this process is to get a database backup of the discourse session you want to examine. Head on over to the admin portal of the discourse session and click on ‘Backups’.
<br>
Click on the blue ‘Backup’ button in the top right to start a new backup. When prompted, select ‘Yes, (do not include uploads)”. Once the backup is finished, it will appear below, with a button that says “Download”. Click this and you will be emailed a download link for the file.
<br>
Once you have this file downloaded, unzip it, rename it ‘discourse.sql’, and place it in the ‘link_checker’ directory.


## Building the Docker Image
Docker allows us to “containerize” the tool and ensure that all of the necessary software libraries are installed no matter which computer is running the script.<br>
If you’d like to learn more about Docker click [here](https://www.docker.com/why-docker). 
To install Docker on your computer click [here](https://www.docker.com/get-started).<br>

Once docker is installed, the next step is to build the Docker image we will be using. Change your working directory to the folder containing the link_checker directory. 
<br>

Once there, call 
```
docker build link_checker -t link_checker:latest  
```
This command points Docker towards the directory containing a Dockerfile (instructions to build a Docker image), in this case that folder is called ‘link_checker’.
<br>
Docker will build your image, installing all of the necessary packages. We are ‘tagging’ the image with the name ‘link_checker:latest’ so that we can easily access it later. You only need to do this step once, unless there are changes to the Dockerfile (environment).


## Instantiating the Docker Container
Now that your image is built, change your working directory to inside the link_checker folder, and instantiate the container with the command:
```
docker run -it --rm --name link_checker -v $(pwd):/home/link_checker link_checker:latest 
```

Briefly, 
docker run link_checker:latest is the command to launch the container
* `-it` means we want to launch it in interactive mode
* `--rm` means we want the container to destroy itself when we exit
* `--name` link_checker gives the container a name
* `-v $(pwd):/home/link_checker` mounts (syncs) your present working directory to the link_checker directory in the container, so that changes to files in the container are reflected on your computer. 



## Building the database from the Discourse Backup
Upon launching, the container will start a postgres database server, create a copy of the database from the discourse.sql file, and run the main.py script that validates the links.
<br>
You will be prompted for the output file name. The program will use this input to build a output csv_file with the output file name and date. 



## Verifying Suspicious Links
If no suspicious links were found, you’re done. 

Otherwise, open the csv you just created (found in finished_searches/) in excel. For each link in the spreadsheet, try to open the link in your web browser. Sometimes sites will appear suspicious because they have guards against robot web crawlers. Opening these links in your web browser will tell you if it is actually broken.

### Broken links
If the link is actually broken, use the contextual information in the spreadsheet to find it on Discourse and fix it.

### Working links
On the other hand, if you click the link and it opens with no problems, add that url to the list of known links in “know_links.json” (comma separated, in quotes). Next time, the link_checker will see that this link has been verified and won’t include it in the list of suspicious links. 



Congratulations, you can now rest easy knowing there are no broken links in your forum. 


