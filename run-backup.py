#!/usr/local/bin/python
import logging
import docker

from os import environ as env

from pathlib import Path
from subprocess import check_output
from subprocess import CalledProcessError

from requests.exceptions import ConnectionError

# Setup logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

logging.info('Starting Docker volume backups...')


# Initialize Docker client
dclient = docker.from_env()

# Collect environment variables
try:
    volume_driver = env['VOLUME_DRIVER']
    backup_retention = env['BACKUP_RETENTION']
    backups_dir = Path(env['BACKUP_DIR'])
    host_dir = Path(env['HOST_DIR'])
    force_backup_flag = (
        '--force' if env['FORCE_BACKUP_CLEANUP'] == 'true' else '')
except KeyError as e:
    logging.critical('Missing environment variable: %s', str(e))
    exit(1)

try:
    # Initialize volume list
    all_volumes = dclient.volumes.list()
except ConnectionError as e:
    logging.critical('Could not connect to the Docker deaemon:')
    logging.critical(e)
    exit(1)

# The volumes that need to be backed up
backup_volumes = []

# Collect the list of volumes with the driver we are backing up
logging.info('The following volumes will be backed up:')
for volume in all_volumes:
    if volume.attrs['Driver'] == volume_driver:
        logging.info(' '*4 + volume.name)
        backup_volumes.append(volume)

# Make sure backups directory exists
if backups_dir.exists() is False or backups_dir.is_dir() is False:
    logging.critical("Backup directory does not exist.")
    exit(1)

# Make sure the `HOST_DIR` exists
if host_dir.exists() is False or host_dir.is_dir() is False:
    logging.critical("HOST_DIR (%s) does not exist.", str(host_dir))
    exit(1)

# Make backups
for volume in backup_volumes:
    volume_mountpoint = host_dir / volume.attrs['Mountpoint'][1:]
    volume_backup_dir = backups_dir/volume.name

    # Run the backup
    try:
        backup_output = check_output(['rdiff-backup', str(volume_mountpoint), str(volume_backup_dir)]).decode()
        if backup_output != '':
            logging.warning(backup_output)
        logging.info('Successfully backed up volume %s', volume.name)
    except CalledProcessError as e:
        logging.error('Something went wrong running backup for volume %s', volume.name)

    # Clean up backups older than the `BACKUP_RETENTION`
    try:
        cleanup_output = check_output(['rdiff-backup', '--remove-older-than', backup_retention, volume_backup_dir]).decode()
        if cleanup_output != '':
            logging.warning(cleanup_output)
        logging.info('Successfully cleaned up old backups for volume %s', volume.name)
    except CalledProcessError as e:
        logging.error('Something went wrong cleaning up backups for volume %s', volume.name)

# All done
logging.info('Done backing up Docker volumes')
