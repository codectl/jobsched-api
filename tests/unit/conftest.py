import pytest

from src.models.job import JobStat, JobSubmit


@pytest.fixture(scope="class")
def qsub_data():
    return {
        "name": "STDIN",
        "queue": "testq",
        "submit_args": "-- /bin/sleep 1000",
        "stdout_path": "/tmp/STDIN.o1",
        "stderr_path": "/tmp/STDIN.e1",
        "resources": {
            "mem": "10gb",
            "cpu": 5,
            "gpu": 2,
            "node_count": 2,
            "place": "pack",
            "walltime": "02:00:00",
        },
        "extra": {
            "account": "pbs_account",
            "project": "_pbs_project_default",
            "priority": 0,
            "flags": {
                "interactive": False,
                "rerunable": True,
                "forward_X11": False,
                "copy_env": False,
            },
            "env": {
                "HOME": "/home/user",
                "SHELL": "/bin/bash",
            }
        }
    }


@pytest.fixture(scope="class")
def qsub_job(qsub_data):
    return JobSubmit.parse_obj(qsub_data)


@pytest.fixture(scope="class")
def qstat_data():
    return {
        "Job_Name": "STDIN",
        "Job_Owner": "testu",
        "resources_used": {
            "cpupercent": 0,
            "cput": "00:00:00",
            "mem": "32gb",
            "ncpus": 24,
            "vmem": "187288kb",
            "walltime": "00:02:00"
        },
        "job_state": "R",
        "queue": "workq",
        "server": "pbs01",
        "Account_Name": "pbs_account",
        "Checkpoint": "u",
        "ctime": "Fri Feb 3 10:41:52 2023",
        "Error_Path": "/home/testu/STDIN.e1",
        "exec_host": "cn01/2*24",
        "exec_vnode": "(cn01:ncpus=24:mem=33554432kb)",
        "Hold_Types": "n",
        "interactive": True,
        "Join_Path": "n",
        "Keep_Files": "n",
        "Mail_Points": "a",
        "Mail_Users": "testu@email.com",
        "mtime": "Fri Feb 3 10:41:52 2023",
        "Output_Path": "/home/testu/STDIN.o1",
        "Priority": 0,
        "qtime": "Fri Feb 3 10:41:53 2023",
        "Rerunable": False,
        "Resource_List": {
            "mem": "32gb",
            "ncpus": 24,
            "nodect": 1,
            "place": "free",
            "select": "1:ncpus=24:mem=32gb",
            "walltime": "24:00:00"
        },
        "stime": "Fri Feb 3 10:42:30 2023",
        "session_id": 16536,
        "jobdir": "/home/testu",
        "substate": 42,
        "Variable_List": {
            "PBS_O_HOME": "/home/testu",
            "PBS_O_LANG": "en_US.UTF-8",
            "PBS_O_LOGNAME": "testu",
            "PBS_O_PATH": "/usr/local/bin:/sbin:/usr/sbin:/usr/local/sbin:/sbin",
            "PBS_O_MAIL": "/var/spool/mail ",
            "PBS_O_SHELL": "/bin/bash",
            "PBS_O_WORKDIR": "/home/testu",
            "PBS_O_SYSTEM": "Linux",
            "PBS_O_QUEUE": "entry",
            "PBS_O_HOST": "ln01.cluster"
        },
        "comment": "Job run on Jan 01 at 00:00 on (cn01:ncpus=24:mem=33554432kb)",
        "etime": "Fri Feb 3 10:41:53 2023",
        "run_count": 1,
        "eligible_time": "00:00:00",
        "Submit_arguments": "-X -I -l select=1:ncpus=24:mem=32gb -l walltime=24:00:00",
        "project": "_pbs_project_default",
        "forward_x11_port": True,
        "Submit_Host": "nn01.cluster"
    }


@pytest.fixture(scope="class")
def qstat_job(qstat_data):
    return JobStat.parse_obj(qstat_data)
