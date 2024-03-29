FROM python:3.9-slim as base

ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONHASHSEED random
ENV DEBIAN_FRONTEND noninteractive

RUN pip install --upgrade pip

WORKDIR /app

FROM base as builder

# install and setup poetry
RUN apt update \
    && apt install -y curl \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
ENV PATH=${PATH}:/root/.local/bin

# package & distribution
COPY src/ src/
COPY pyproject.toml poetry.lock ./
COPY README.rst .env* ./
RUN python -m venv /venv
RUN . /venv/bin/activate && poetry install --no-interaction --no-dev --no-root
RUN . /venv/bin/activate && poetry build

FROM base

# install system dependencies
RUN apt update \
    && apt install -y sudo \
    # identity discovery modules
    && apt install -y libsasl2-dev libldap2-dev libssl-dev \
    && apt install -y libnss-ldapd libpam-ldapd ldap-utils \
    # additional required libs
    && apt install -y munge libmunge-dev

# system configurations
COPY etc/sudoers.d/ /etc/sudoers.d/
COPY etc/nslcd.conf /etc/
COPY etc/nsswitch.conf /etc/
COPY etc/pbs.conf /etc/
RUN chmod 0700 /etc/sudoers.d/
RUN chmod 0700 /etc/nslcd.conf
RUN chmod 0755 /etc/nsswitch.conf
RUN chmod 0544 /etc/pbs.conf

# create system user
ENV USER jobsched-api
ENV UID 1000
ENV GID 1000
RUN useradd --system -u $UID $USER

COPY src/ src/
COPY bootstrap .
COPY --from=builder /app/dist .
RUN pip install *.whl

RUN chown -R $UID:$GID .
RUN chmod -R 0500 .

# run process as non root
USER $USER

# include bin in PATH
ENV PATH $PATH:/opt/pbs/bin

# command to run on container start
ARG env="production"
ENV ENV $env
CMD ./bootstrap && gunicorn --bind 0.0.0.0:5000 "src.app:create_app('${ENV}')"
