import os

import requests


# edit these variables accordingly
base_url = "http://localhost:5000/api/jobsched/v1"
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

# POST request to create job
r = requests.post(
    url=f"{base_url}/pbs/qsub",
    auth=(username, password),
    json={
        "name": "STDIN",
        "queue": "testq",
        "submit_args": "-- /bin/sleep 10",
        "resources": {
            "mem": "10gb",
            "cpu": 1,
            "gpu": 1,
            "node_count": 1,
            "place": "pack",
            "walltime": "00:02:00",
        },
    },
)
assert r.status_code == 200
