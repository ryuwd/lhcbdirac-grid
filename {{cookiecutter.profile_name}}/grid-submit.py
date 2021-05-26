#!/usr/bin/env python3

import tempfile
import textwrap
import sys
import subprocess
import os
import getpass
import json
import shutil
import glob

from snakemake.utils import read_job_properties


def wait_for_proxy():
    print("Your grid proxy has expired. Please create a new proxy (lhcb-proxy-init).", file=sys.stderr)

    # call lhcb-proxy-init


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

commit = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, check=True).stdout.decode().strip()
source = ".grid-source-{}.tar".format(commit)

if not os.path.exists(source):
    for f in glob.glob(".grid-source-*.tar"):
        os.remove(f)
    subprocess.run(["git", "archive", "--format", "tar", "-o", source, "HEAD"], check=True)


with tempfile.TemporaryDirectory() as jobdir:
    jobsubpath = os.path.join(jobdir, "dirac-jobsub.py")

    {% raw %}
    with open(jobsubpath, "w") as jobsub:
        jobsub.write(textwrap.dedent("""
    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC.Interfaces.API.Job import Job

    j = Job()
    j.setExecutable("/bin/bash", arguments="jobscript.sh", logFile='job_{RuleName}_{JobID}.log')
    j.setInputSandbox(['jobscript.sh', 'grid-source.tar'])
    j.setOutputSandbox(['std.out', 'std.err', 'job_{RuleName}_{JobID}.log'])
    j.setCPUTime({CPUTime})
    j.setNumberOfProcessors({NumberOfProcessors})
    j.setDestination({Destination})
    j.setBannedSites({BannedSites})
    j.setName('snakemake rule {RuleName} jobID {JobID}')
    print (Dirac().submitJob(j))

    """).format(
        CPUTime=job_properties["resources"].get("CPUTime", 240),
        NumberOfProcessors=job_properties["threads"],
        BannedSites=repr(job_properties["resources"].get("BannedSites", [])),
        Destination=job_properties["resources"].get("Destination", "ANY"),
        RuleName=job_properties["rulename"],
        JobID=job_properties["jobid"],
    )
    {% endraw %}

    shutil.copyfile(jobsubpath, "last-jobsub.py")
    shutil.copyfile(jobscript, "last-jobscript.sh")
    shutil.copyfile(jobscript, os.path.join(jobdir, "jobscript.sh"))
    shutil.copyfile(source, os.path.join(jobdir, "grid-source.tar"))

    workdir = os.getcwd()
    os.chdir(jobdir)
    cmd = ["lb-dirac", "python", jobsub.name]

    for i in range(10):
        try:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
            break
        except subprocess.CalledProcessError as e:
            if "No proxy found" in e.stdout.decode():
                wait_for_proxy()
                raise e

    jobID = res.stdout.decode().strip()
    os.chdir(workdir)

# print jobid for use in Snakemake
print(jobID)
