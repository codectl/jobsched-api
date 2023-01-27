import pytest

from src.models.job import Job, JobStatus


@pytest.fixture(scope="class")
def raw_data():
    return {
        "timestamp": 1479277336,
        "pbs_version": "14.1",
        "pbs_server": "vbox",
        "Jobs": {
            "1.vbox": {
                "Job_Name": "STDIN",
                "Job_Owner": "user@vbox",
                "job_state": "Q",
                "queue": "workq",
                "server": "vbox",
                "Checkpoint": "u",
                "ctime": "Fri Nov 11 17:57:05 2022",
                "Error_Path": "/tmp/STDIN.e1",
                "Hold_Types": "n",
                "Join_Path": "n",
                "Keep_Files": "n",
                "Mail_Points": "a",
                "mtime": "Fri Nov 11 17:57:05 2022",
                "Output_Path": "/tmp/STDIN.o1",
                "Priority": 0,
                "interactive": False,
                "qtime": "Fri Nov 11 17:57:05 2022",
                "Rerunable": True,
                "Resource_List": {
                    "ncpus": 1,
                    "nodect": 1,
                    "place": "pack",
                    "select": "1:ncpus=1"
                },
                "schedselect": "1:ncpus=1",
                "substate": 10,
                "Variable_List": {
                    "PBS_O_HOME": "/root",
                    "PBS_O_LANG": "en_US.utf8",
                    "PBS_O_LOGNAME": "user",
                    "PBS_O_PATH": "/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin",
                    "PBS_O_MAIL": "/var/spool/mail/user",
                    "PBS_O_SHELL": "/bin/bash",
                    "PBS_O_WORKDIR": "/home/user/Tasks/overlay",
                    "PBS_O_SYSTEM": "Linux",
                    "PBS_O_QUEUE": "workq",
                    "PBS_O_HOST": "vbox"
                },
                "euser": "root",
                "egroup": "root",
                "queue_rank": 1,
                "queue_type": "E",
                "comment": "Not Running: Not enough free nodes available",
                "etime": "Fri Nov 11 17:57:05 2022",
                "Submit_arguments": "-- /bin/sleep 1000",
                "executable": "<jsdl-hpcpa:Executable>/bin/sleep</jsdl-hpcpa:Executable>",
                "argument_list": "<jsdl-hpcpa:Argument>1000</jsdl-hpcpa:Argument>",
                "project": "_pbs_project_default",
                "Account_Name": "pbs_account",
            }
        }
    }


def test_job_deserializer(raw_data):
    job_data = next(iter(raw_data["Jobs"].values()))
    job = Job.parse_obj(job_data)
    assert job.name == "STDIN"
    assert job.owner == "user@vbox"
    assert job.status == JobStatus.QUEUE
    assert job.queue == "workq"
    assert job.server == "vbox"
    assert job.submit_args == "-- /bin/sleep 1000"
    assert job.stdout_path == "/tmp/STDIN.o1"
    assert job.stderr_path == "/tmp/STDIN.e1"
    assert job.resources.select == "1:ncpus=1"
    assert job.resources.cpu == 1
    assert job.resources.node_count == 1
    assert job.resources.place == "pack"
    assert job.comment == "Not Running: Not enough free nodes available"
    assert job.account == "pbs_account"
    assert job.project == "_pbs_project_default"
    assert job.interactive is False
    assert job.rerunable is True
