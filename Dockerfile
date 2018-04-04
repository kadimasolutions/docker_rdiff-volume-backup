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

COPY run-backup.py /run-backup.py
RUN chmod 744 /run-backup.py

COPY docker-cmd.sh /docker-cmd.sh
RUN chmod 744 /docker-cmd.sh

CMD /docker-cmd.sh
