*************
Kustomization
*************

Refer to the `main <https://github.com/codectl/microservices.git#kustomization>`__
repository.

Directory structure
===================
Refer to the
`main <https://github.com/codectl/microservices.git#directory-structure>`__
repository.

Secret management
=================
There are no secrets needed to manage on this project.

Usage
=====
Refer to the `main <https://github.com/codectl/microservices.git#usage>`__
repository.

Upon following those steps, the ``pods`` should be running (or about to). An example
output with default settings:

.. code-block:: bash

    $ kubectl get pods
    NAME                       READY   STATUS      RESTARTS    ...
    jobsched-api-XXX-XXX       1/1     Running     0           ...
    jobsched-api-XXX-XXX       1/1     Running     0           ...
