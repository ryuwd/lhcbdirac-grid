#!/bin/bash
# properties = {properties}

set -e

user=$2

source /cvmfs/lhcb.cern.ch/lib/LbEnv
ENV_PREFIX="lb-conda default "

#xport PATH=/cvmfs/softdrive.nl/$user/Miniconda2/bin:$PATH
echo "hostname:"
hostname -f


tar -xf grid-source.tar

$ENV_PREFIX {exec_job}
echo $?
