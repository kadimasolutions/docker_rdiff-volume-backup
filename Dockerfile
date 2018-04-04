FROM python:3-alpine

# Environment variable defaults
ENV VOLUME_DRIVER local
ENV CRON_SCHEDULE 0 0 * * *
ENV BACKUP_RETENTION 12M
ENV BACKUP_DIR /backup

# Install the python Docker library
RUN pip3 install docker

# Install `rdiff-backup`
RUN apk add --no-cache rdiff-backup

# Copy in backup script
COPY run-backup.py /run-backup.py
RUN chmod 744 /run-backup.py

# Copy in container startup script
COPY docker-cmd.sh /docker-cmd.sh
RUN chmod 744 /docker-cmd.sh

# Set the Docker command
CMD /docker-cmd.sh
