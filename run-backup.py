#!/usr/local/bin/python
from os import environ as env
import docker

# Initialize Docker client
dclient = docker.from_env()

# Initialize volume list
volumes = []

# List docker volumes of the VOLUME_DRIVER
driver = env['VOLUME_DRIVER']
for volume in dclient.volumes.list():
    if volume.attrs['Driver'] == driver:
        volumes.append(volume)
