# Docker rdiff-volume-backup

This is a Docker image that is meant to be used to backup your Docker volumes using the [rdiff-backup](http://rdiff-backup.nongnu.org/) tool for incremental backups. If you want to backup a host directory instead of Docker volumes, [tozd/rdiff-backup](https://hub.docker.com/r/tozd/rdiff-backup/) would be a more suitable container.

## Usage

### Summary

This container needs to mount the Docker socket to get the list of Docker volumes of the specified `VOLUME_DRIVER`, which is `local` by default. The directory containing the volumes for that particular driver also needs to be mounted. Finally, you need to bind mount a host directory or a Docker volume ( with a different driver than the volumes that you want to back up ) to the `/backup` directory to persist the backups.

 Backups will be run on the given `CRON_SCHEDULE` which is `0 0 * * *` ( daily at 12:00am ) by default. Rdiff will keep diffs that allow you to reproduce any backup up to the `BACKUP_RETENTION` time period which is `12M` ( 12 months ) by default.

A Docker Compose file would look like this:

**docker-compose.yml**
```yml
version: '2'
services:
  rdiff-volume-backup:
    image: kadimasolutions/rdiff-volume-backup
    volumes:
     - /var/run/docker.sock:/var/run/docker.sock
     # This will be different for different volume drivers and Docker
     # configurations
     - /var/lib/docker/volumes:/host/var/lib/docker/volumes
     # Bind mount a host directory to persist backups OR
     - /backup:/backup
     # Mount a docker volume with a different driver
     #- volume-backups:/backup
    environment:
      VOLUME_DRIVER: local
      CRON_SCHEDULE: 0 0 * * *
      BACKUP_RETENTION: 12M

# Uncomment if using Docker volume to persist backups
#volumes:
  #volume-backups:
    #driver: docker-volume-driver-that-is-not-the-same-as-VOLUME_DRIVER
```

### Identifying the Docker Volume mountpoint

In order for the container to have access to the Docker volumes, the directory containing the Docker volume mountpoints needs to be mounted into the container. This directory can be different depending on your Docker configuration and the volume driver. To find out the volume directory for your particular config and driver first run `docker volume ls` to get the list of docker volume on your host.

```
$ docker volume ls
DRIVER              VOLUME NAME
local               4d3b80341630e9f114e845ccbbe483b0b24595c31d2feeac37ec2df4719a83c2
local               795cd38166cd483f305ab27056d82da20efcfc4a0170295c6573bc76b5e17dae
rancher-nfs         ad520ada61447252479e5f1e0a6f4a3c478ab6d06e9ca218c54992c192e99d09
```

Next pick a volume with the driver that you want to backup and run `docker volume inspect <volume-name>`.

```
$ docker volume inspect 4d3b80341630e9f114e845ccbbe483b0b24595c31d2feeac37ec2df4719a83c2
[
    {
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/mnt/sda1/var/lib/docker/volumes/4d3b80341630e9f114e845ccbbe483b0b24595c31d2feeac37ec2df4719a83c2/_data",
        "Name": "4d3b80341630e9f114e845ccbbe483b0b24595c31d2feeac37ec2df4719a83c2",
        "Options": {},
        "Scope": "local"
    }
]
```

We are specifically interested in the `Mountpoint` key. The directory that we need to mount into the container is the directory that contains all of the docker volumes of this volume driver. In this case that is `/mnt/sda1/var/lib/docker/volumes/`. This directory should be mounted into the container with the `/host` prefix: `/host/mnt/sda1/var/lib/docker/volumes/`.

### Environment Variables

The full list of environment variables.

#### VOLUME_DRIVER

The `VOLUME_DRIVER` tells the container what type of Docker volume to backup. All volume of the specified driver will be backed up.

**Default:** `local`

#### CRON_SCHEDULE

The `CRON_SCHEDULE` is the schedule on which the backup script will be executed.

**Default:** `0 0 * * *` ( Run daily at 12:00am )

#### BACKUP_RETENTION

The `BACKUP_RETENTION` is the length of time that the backup history is kept. Any backups older than the specified time will be deleted when a new backup is made. The details of the time format can be found on the [rdiff-backup man page](https://github.com/sol1/rdiff-backup/blob/8ccc5a3b44c996ecd810f8d5d586d0da6435cc32/rdiff-backup/rdiff-backup.1#L601).

**Default:** `12M` ( 12 months )

#### BACKUP_DIR

The directory in the container to make backups to. In order for the backups to be useful, you must either bind mount a host directory or mount a docker volume ( with a different driver than the one that you are backup up ) to this path in order to persist the backups.

**Default:** `/backup`
