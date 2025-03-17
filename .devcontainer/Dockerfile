FROM mcr.microsoft.com/devcontainers/python:3.11

# Install additional system dependencies if needed
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    net-tools \
    iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
WORKDIR /workspace
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && pip3 --disable-pip-version-check --no-cache-dir install ruff pyright \
    && rm -rf /tmp/pip-tmp

# Setup a non-root user with sudo access
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Make sure we have the right permissions for the workspace
RUN mkdir -p /workspace && chown $USER_UID:$USER_GID /workspace 