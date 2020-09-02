# Curie-Web

![Backend Tessts](https://github.com/navanchauhan/Curie-Web/workflows/Test%20Backend/badge.svg)
![Database Tests](https://github.com/navanchauhan/Curie-Web/workflows/Test%20Database/badge.svg)
[![DeepSource](https://static.deepsource.io/deepsource-badge-dark-mini.svg)](https://deepsource.io/gh/navanchauhan/Curie-Web/?ref=repository-badge) 

Tested on: 
* macOS 10.15 (Catalina)
* Ubuntu 20.04 - Raspberry Pi 4

**Do Not Forget To Change DB Host configuration!**

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

Replace the values in `app/__init__.py`, `app/dock-single.py` and `app/dock-docker.py`

## 3. Enabling LSTM Generator

Open `app/views.py`

Make sure you have installed Tensorflow. Replace the following:

```python
tfWorking = 0
```

with

```python
tfWorking = -1
```

## 4. Adding AR Model Support

Make sure you have PyMOL 2.0 or higher


Either download the precompiled binaries from  [COLLADA2GLTF](https://github.com/KhronosGroup/COLLADA2GLTF) or compile it on your own


Once you have the `COLLADA2GLTF-bin` file, run the following:

```
cp COLLADA2GLTF-bin /usr/local/bin/collada2gltf
```          

## Running 

### Without FastAPI

`gunicorn api:app -b "0.0.0.0:7589"`

### With FastAPI

`gunicorn api:app -k uvicorn.workers.UvicornWorker -b "0.0.0.0:7589"`