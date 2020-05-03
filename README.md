# README

### Docker pull command

`docker pull destro97/youtube-stock:latest`

### Docker run command

`docker run -t --name youtube-container -p 8000:8000 destro97/youtube-stock:latest`

### Docker container stop command

`docker stop youtube-container`



# Testing Steps

- First pull the docker image using above command.
- Next run the container with the pulled image using above command.
- After running the container, open localhost:8000 on your browser.
- You will have to wait for 10 seconds after first server run to get some data to be viewed on the browser because of Scheduled task to store YouTube Data into DB.
- You can search in the search bar provided in the top left of the page.
- Be sure to stop the container using above command after completing your testing. This step is necessary to conserve the Google API KEY Quota available.
- The project can also be run on local machine directly by cloning the repo and running command:

`python manage.py migrate && python manage.py runserver`
