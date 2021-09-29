FROM python:3.7-alpine

# this is so scim user can run sudo and sqlalchemy build
RUN apk add sudo supervisor gcc build-base postgresql-dev

# Create app user for correct file permissions
ARG US_ID=1000
ARG GR_ID=1000
ARG USERNAME=ytdl

RUN addgroup --gid $GR_ID $USERNAME
RUN adduser --disabled-password --gecos '' --uid $US_ID -G $USERNAME $USERNAME

# allow user to run sudo commands without password - might want to delete this at some
RUN chmod 644 /etc/sudoers && \
    echo "$USERNAME     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER $USERNAME

# Copy supervisor config files
COPY --chown=$USERNAME supervisord/supervisord.conf /etc/supervisord.conf
COPY --chown=$USERNAME supervisord/services.conf /etc/supervisor/conf.d/

RUN mkdir /home/$USERNAME/app
WORKDIR /home/$USERNAME/app
COPY --chown=$USERNAME . .
RUN pip install -r requirements.txt

ENV PATH="/home/$USERNAME/.local/bin:$PATH"

ENTRYPOINT ["./entrypoint.sh", "api"]