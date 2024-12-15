<div align="center">

  <a href="">[![Pytest Testing Suite](https://github.com/diverso-lab/uvlhub/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/diverso-lab/uvlhub/actions/workflows/tests.yml)</a>
  <a href="">[![Commits Syntax Checker](https://github.com/diverso-lab/uvlhub/actions/workflows/commits.yml/badge.svg?branch=main)](https://github.com/diverso-lab/uvlhub/actions/workflows/commits.yml)</a>
  
</div>

<div style="text-align: center;">
  <img src="https://www.uvlhub.io/static/img/logos/logo-light.svg" alt="Logo">
</div>

# Getting started with Gazpacho-hub

Follow this guide to set up the project:

### 1. Clone the repository
- Clone Gazpacho-hub repository by executing `git@github.com:EGC-Gazpacho/gazpacho-hub.git` in the directory of your choice. Remembering to create a ssh key first.

### 2. Configure the  environment
#### Linux
- Install mariadb `sudo apt install mariadb-server -y`.
- Start mariadb `sudo systemctl start mariadb`.
- Configure MariaDB `sudo mysql_secure_installation`, accepting every step.

##### Configure databases and users
 
- Configure database `sudo mysql -u root -p`, using uvlhubdb_root_password as root password.

```bash
#!/bin/bash

CREATE DATABASE uvlhubdb;
CREATE DATABASE uvlhubdb_test;
CREATE USER 'uvlhubdb_user'@'localhost' IDENTIFIED BY 'uvlhubdb_password';
GRANT ALL PRIVILEGES ON uvlhubdb.* TO 'uvlhubdb_user'@'localhost';
GRANT ALL PRIVILEGES ON uvlhubdb_test.* TO 'uvlhubdb_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

```

##### Configure app environment

- Environment variables `cp .env.local.example .env`
- Ignore webhook module `echo "webhook" > .moduleignore`


##### Install dependencies

###### Creates and activate a virtual environment

- Install virtualenv `sudo apt install python3.12-venv`
- In the root directory of the project you just cloned, create the virtual environment by running  `python3.12 -m venv venv` , venv being what you want to name the virtual environment.
- Activate your new virtual environment with  ´source venv/bin/activate´


###### Install Python dependencies
- `pip install --upgrade pip`
- `pip install -r requirements.txt`


###### Install Python dependencies

- Install it in editable mode `pip install -e ./`

- To check that Rosemary has been installed correctly `rosemary`


##### Run app
- Apply migrations `flask db upgrade`
- Populate database `rosemary db:seed`
- Run development Flask server `flask run --host=0.0.0.0 --reload --debug`

 
## Official documentation

You can consult the official documentation of the project at [docs.uvlhub.io](https://docs.uvlhub.io/)
