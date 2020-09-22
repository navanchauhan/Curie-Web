# Curie-Web

![Database and Backend](https://github.com/navanchauhan/Curie-Web/workflows/Test%20Database%20and%20Backend/badge.svg)

![Curie-Web Cover](./misc/Title.png)

Tested on: 
* macOS 10.15 (Catalina)
* Ubuntu 20.04 - Raspberry Pi 4

# Quick Start (Docker-Compose)

You can quickly get started and test Curie-Web without needing to manage dependencies by using the `docker-compose` image. This has all features except AR/3D Model support and should be production ready.


```
git clone https://github.com/navanchauhan/Curie-Web
cd Curie-Web
docker-compose up
```

Do not forget to edit `config.ini` for the email section. Do not change the database settings for running it via docker. 

## Caveat(s):

* This does not support generating a 3D Model and thus, AR viewer will not work on the Job Status page.

# Installation

## 1. Installing Dependencies

### 1.1 Docker

Once you have installed docker, make sure to pull the following images (Otherwise, these will automatically get downloaded when you run the web-server)

* navanchauhan/curie-cli (amd64/aarch64)
* navanchauhan/usd-from-gltf (aarch64)
* leon/usd-from-gltf (amd64)

### 1.2 PLIP

Install from [pharmai/plip](https://github.com/pharmai/plip). 

In case you have problems installing it, install it from the forked repo [navanchauhan/plip](https://github.com/navanchauhan/plip)

### 1.3 PyMOL with Python Bindings (version >= 2.0)

* macOS users can use Homebrew to install it via `brew install pymol`

* Users using apt can install it via `sudo apt install pymol`

### 1.4 Open-Babel (version >= 3.0)

macOS users can use Homebrew to install it via `brew install open-babel`

Users using apt can install it via `sudo apt install openbabel python3-openbabel`

## 2. Changing the Configuration

Replace the values in `config.ini`

Default Values:
```ini
[DATABASE]
HOST = navanspi.duckdns.org
PORT = 3306
USER = curieweb
PASSWORD = curie-web-russian-54
NAME = curie

[SMTP]
SERVER = smtp.gmail.com
PORT = 587
EMAIL = navanchauhan@gmail.com
PASSWORD = okrs shoc ahtk idui

[LOGS]
LOG = True
SAVE_LOGS = False 

[FILES]
UPLOAD_FOLDER = ./app/static/uploads
LOG_FOLDER = ./app/logs/

[EXECUTION]
INSTANT = True

[FEATURES]
LSTM = False
```

### **Database**
| Name     | Description         |
|----------|---------------------|
| HOST     | MySQL Database Host |
| PORT     | MySQL Database Port |
| USER     | Username            |
| PASSWORD | Password            |
| NAME     | MySQL Database Name |

### **SMTP**
| Name     | Description |
|----------|-------------|
| SERVER   | SMTP Server |
| PORT     | SMTP Port   |
| EMAIL    | Email       |
| PASSWORD | Password    |

### **LOGS**
| Name      | Description |
|-----------|-------------|
| LOG       | Log         |
| SAVE_LOGS | SAVE LOGS   |

### **FILES**
| Name          | Description           |
|---------------|-----------------------|
| UPLOAD_FOLDER | Folder to store files |
| LOG_FOLDER    | Folder to store logs  |

### **EXECUTION**
| Name          | Description           |
|---------------|-----------------------|
| INSTANT | Whether to run the docking jobs instantly (True or False) |

### **FEATURES**
| Name          | Description           |
|---------------|-----------------------|
| LSTM | Enable LSTM Generator (True or False) |


## 3. Adding AR Model Support

Make sure you have PyMOL 2.0 or higher


Either download the precompiled binaries from  [COLLADA2GLTF](https://github.com/KhronosGroup/COLLADA2GLTF) or compile it on your own


Once you have the `COLLADA2GLTF-bin` file, copy the file:

```
cp COLLADA2GLTF-bin /usr/local/bin/collada2gltf
```          

## 4. Setting up the Database

You will first need to create a database and grant all priviliges to a user. Make sure you have correctly configured the `config.ini` file. 

After tha simply run the following commands. This will create the table(s) and check if the backend is working or not.

```
cd tests
python3 dbTestFiller.py
python3 backendTest.py
python3 removeSample.py
```

## 5. Running 

### Without FastAPI

`gunicorn api:app -b "0.0.0.0:7589"`

### With FastAPI

`gunicorn api:app -k uvicorn.workers.UvicornWorker -b "0.0.0.0:7589"`

### systemd

**There is a sample systemd file in the misc folder**

* Configure the file and then copy it to `/etc/systemd/system`

* You can start the server by running `sudo systemctl start curie`

* To enable the server to start on boot run `sudo systemctl enable curie`

