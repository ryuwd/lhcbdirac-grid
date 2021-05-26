#!/usr/bin/env python

import json
import subprocess
import sys
import time


def wait_for_proxy():
    stdout = sys.stdout
    sys.stdout = sys.stderr
    input(
        "UI proxy expired. Please create a new proxy (see README) and press ENTER to continue."
    )
    sys.stdout = stdout


STATUS_ATTEMPTS = 20

jobid = sys.argv[1]

# try to get status 10 times
for i in range(STATUS_ATTEMPTS):
    try:
        res = subprocess.run(
            ["lb-dirac", "dirac-wms-job-status", "{}".format(jobid)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        res = json.loads(res.stdout.decode())["Value"]
        if not res["OK"]:
            continue
        break
    except subprocess.CalledProcessError as e:
        if "No proxy found" in e.stdout.decode():
            wait_for_proxy()
            continue
        if i >= STATUS_ATTEMPTS - 1:
            # if "already purged" in e.stdout.decode():
            #     # we know nothing about this job, so it is safer to consider
            #     # it failed and rerun
            #     print("failed")
            #     exit(0)
            print("lb-dirac dirac-wms-job-status error: ", e.stdout, file=sys.stderr)
            raise e
        else:
            time.sleep(5)


status = res[jobid]["Status"]
minorstatus = res[jobid]["MinorStatus"]
if status == "Done" and minorstatus == "Execution Complete":
    print("success")
elif status == "Failed":
    print("failed")
elif status.startswith("Done"):
    print("failed")
elif status == "Killed":
    print("failed")
elif status == "Aborted":
    print("failed")
elif status == "Cleared":
    print("failed")
else:
    print("running")
