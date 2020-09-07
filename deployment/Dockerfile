# Base image
FROM python:3.7.6-alpine3.11

# For aiohttp multidict installation error below line is required
RUN apk add build-base

ARG USER=aiohttp
ARG GROUP=aiohttp

# # We cannot set as root because it will affect when we try to mount the volume
ARG HOME=/home/${USER}
ENV APP_DIR=${HOME}/app
ENV LOCAL_BIN=${HOME}/.local/bin
ENV PATH="${PATH}:${LOCAL_BIN}"
ENV HOST=0.0.0.0
ENV PORT=8080

RUN apk add openssl curl ca-certificates bash \
        && apk add ssmtp

# # Create an user for security issues (256000 - Last id)
RUN addgroup -g 256000 ${GROUP} && \
    adduser -D -u 256000 -G ${USER} ${GROUP} && \
    chown -R ${USER}:${GROUP} ${HOME}

COPY . ${APP_DIR}
RUN chown -R ${USER}:${GROUP} ${APP_DIR}

USER ${USER}

WORKDIR ${APP_DIR}


# Install the python packages
RUN pip install pipenv setuptools --user
RUN pipenv lock -r | tail -n +2 > requirements.txt
RUN pip install -r requirements.txt --user

# Start #
COPY entrypoint.sh /usr/local/bin
CMD ["entrypoint.sh"]