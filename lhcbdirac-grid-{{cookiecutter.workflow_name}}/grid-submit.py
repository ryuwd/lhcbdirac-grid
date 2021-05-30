#!/usr/bin/env python3

import tempfile
import textwrap
import sys
import subprocess
import os
import json
import shutil
import glob
import stat

from snakemake.utils import read_job_properties


def wait_for_proxy():
    raise RuntimeError(
        "Your grid proxy has expired. Please create a new proxy (lhcb-proxy-init) and re-launch snakemake to resume job submission.",
    )


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

commit = (
    subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, check=True)
    .stdout.decode()
    .strip()
)
source = ".grid-source-{}.tar".format(commit)
snakemake_conda = "snakemake-grid.tar"

if not os.path.exists(source):
    for f in glob.glob(".grid-source-*.tar"):
        os.remove(f)
    subprocess.run(
        ["git", "archive", "--format", "tar", "-o", source, "HEAD"], check=True
    )

if os.path.exists(".use-conda-prepared"):
    use_conda_input = ""

with tempfile.TemporaryDirectory() as jobdir:
    jobsubpath = os.path.join(jobdir, "dirac-jobsub.py")

    lfns = ["/" + lfn for lfn in job_properties["input"]]
    with open(jobsubpath, "w") as jobsub:
        jobsub.write(
            textwrap.dedent(
            {% raw %}
                """
        from DIRAC.Interfaces.API.Dirac import Dirac
        from DIRAC.Interfaces.API.Job import Job
        import json, os
        from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb
        from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob

        # upload snakemake conda environment with patched version,
        # and snakemake conda environments.
        snakemake_input = [
            "LFN:/{storage_prefix}/snakemake-grid.tar", 
            "LFN:/{storage_prefix}/snakemake-envs.tar"
        ]

        j = Job()
        # we rely on snakemake to upload output to the right LFN / location
        # j.setInputData([])
        j.setInputData({InputData} + [snakemake_input])
        j.setExecutable("jobscript.sh", logFile='job_{RuleName}_{JobID}.log')
        j.setInputSandbox(['jobscript.sh', 'grid-source.tar'] + {InputData} + snakemake_input)
        j.setOutputSandbox(['std.out', 'std.err', 'job_{RuleName}_{JobID}.log'])
        j.setCPUTime({CPUTime})
        j.setNumberOfProcessors({NumberOfProcessors})
        if '{Destination}' != 'ANY': j.setDestination('{Destination}')
        if len({BannedSites}) > 0: j.setBannedSites({BannedSites})
        j.setName('snakemake rule {RuleName} jobID {JobID}')
        sub_info = (Dirac().submitJob(j))
        print (json.dumps(sub_info))

        """
        {% endraw %}
            ).format(
                storage_prefix="{{ cookiecutter.grid_storage_prefix }}",
                CPUTime=job_properties["resources"].get("CPUTime", 240),
                NumberOfProcessors=job_properties["threads"],
                BannedSites=repr(job_properties["resources"].get("BannedSites", [])),
                Destination=job_properties["resources"].get("Destination", "ANY"),
                RuleName=job_properties["rule"],
                JobID=job_properties["jobid"],
                InputData=repr(
                    ["LFN:" + l for l in lfns]
                ),  # LFNs to download into the job
            )
        )
    jscript2 = os.path.join(jobdir, "jobscript.sh")
    with open(jobscript, "r") as f:
        script = f.read().replace("[[LFNS]]", " ".join(lfns))
        with open(jscript2, "w") as f2:
            f2.write(script)
    st = os.stat(jscript2)
    os.chmod(jscript2, st.st_mode | stat.S_IEXEC)

    shutil.copyfile(jobsubpath, "last-jobsub.py")
    shutil.copyfile(jscript2, "last-jobscript.sh")
    shutil.copyfile(source, os.path.join(jobdir, "grid-source.tar"))
    # shutil.copyfile(snakemake_conda, os.path.join(jobdir, "snakemake-grid.tar"))

    workdir = os.getcwd()
    os.chdir(jobdir)
    cmd = ["lb-dirac", "python", jobsub.name]

    for i in range(10):
        try:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
            if "No proxy found" in res.stdout.decode():
                wait_for_proxy()
                continue
            break
        except subprocess.CalledProcessError as e:
            if "No proxy found" in e.stdout.decode():
                wait_for_proxy()
                raise e
    try:
        jobInfo = json.loads(res.stdout.decode().strip())
    except json.decoder.JSONDecodeError as e:
        print("Got bad output from lb-dirac submission script:", file=sys.stderr)
        print(res.stdout.decode().strip(), file=sys.stderr)
        raise e
    jobID = jobInfo["JobID"]
    os.chdir(workdir)

# print jobid for use in Snakemake
print(jobID)
