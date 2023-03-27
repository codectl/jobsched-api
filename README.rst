************
jobsched-api
************

.. image:: https://img.shields.io/docker/v/renatodamas/jobsched-api?logo=docker
    :target: https://hub.docker.com/repository/docker/renatodamas/jobsched-api
    :alt: docker
.. image:: https://github.com/codectl/jobsched-api/actions/workflows/ci.yaml/badge.svg
    :target: https://github.com/codectl/jobsched-api/actions/workflows/ci.yaml
    :alt: CI
.. image:: https://codecov.io/gh/codectl/jobsched-api/branch/master/graph/badge.svg
    :target: https://app.codecov.io/gh/codectl/jobsched-api/branch/master
    :alt: codecov
.. image:: https://img.shields.io/badge/OAS-2_|_3-14ACBB.svg
    :target: https://github.com/OAI/OpenAPI-Specification
    :alt: OpenAPI Specification 2/3 compatible
.. image:: https://img.shields.io/github/pipenv/locked/python-version/codectl/jobsched-api
    :target: https://github.com/codectl/jobsched-api
    :alt: Python compatibility
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: code style: black
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: license: MIT

A RESTful API service for scheduling interactive and non-interactive (batch) jobs in a computer cluster. The service
facilitates the communication with the cluster job scheduler by providing a simple and clean interface that abstracts
the complexity that is typically involved when dealing with a cluster scheduler. The 2 most common operations pertaining
job scheduling are job composition and submission (``qsub``) and querying a job for its status (``qstat``).

The service currently supports ``OpenPBS`` and ``PBSPro`` as a job scheduler.

Setup 🔧
========
The application can run in several ways, depending on what the target platform is.
One can run it directly on the system with ``python`` or get it running on a
``kubernetes`` cluster.

Python
------
The project uses `poetry <https://python-poetry.org/>`__ for dependency management
. Therefore to set up the project (recommended):

.. code-block:: bash

    # ensure poetry is installed
    $ poetry env use python3
    $ poetry install

That will configure a virtual environment for the project and install the respective
dependencies, which is particular useful during development stage.

Kubernetes
----------
Refer to `README <.kustomization/README.rst>`__ under ``.kustomization/``.

Configuration 📄
----------------
Since the project can read properties from the environment, one can use an ``.env``
file for application configurations. These should be set accordingly for a correct
service usage.

A possible configuration is:

.. code-block:: bash

    # Application context
    APPLICATION_CONTEXT=/api/jobsched/v1

    # version of OpenAPI
    OPENAPI=3.0.3


Note ⚠️: one should use ``configmap`` and ``secret`` instead when configuring it for
``kubernetes``.

Run 🚀
======
For a quick run with ``Flask``, run it like:

.. code-block:: bash

    $ poetry run flask run

Configure ``flask`` environments with environment variables or in a ``.flaskenv`` file.

``Flask`` uses ``Werkzeug`` which is a ``WSGI`` library intended for development
purposes. Do not use it in production! For a production like environment, one should
use instead a production server, like ``gunicorn``:

.. code-block:: bash

    $ poetry run gunicorn src.app:create_app

Tests & linting 🚥
==================
Run tests with ``tox``:

.. code-block:: bash

    # ensure tox is installed
    $ tox

Run linter only:

.. code-block:: bash

    $ tox -e lint

Optionally, run coverage as well with:

.. code-block:: bash

    $ tox -e coverage

License
=======
MIT licensed. See `LICENSE <LICENSE>`__.
