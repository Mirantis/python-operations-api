==============
Operations API
==============


Overview
--------

API for generating and manage UI forms for reclass model templates

Requirements
------------

-  Python v3.6 and higher.
-  Pip v3 and higher.

Installation notes
------------------

- Start backend services (CockroachDB, Keycloak)

  ::

    ./bootstrap_env.sh up

- Tested with:

   - Docker 17.03.2-ce
   - Docker Compose 1.22.0

- Prepare python virtual environment

  ::

    python -m ensurepip --default-pip
    pip install --user pipenv
    pipenv --python 3.6
    pipenv install
    pipenv shell

    python operations_api



