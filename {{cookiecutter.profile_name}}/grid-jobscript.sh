#!/bin/bash
# properties = {properties}

set -e

user=$2

source /cvmfs/lhcb.cern.ch/lib/LbEnv
ENV_PREFIX="lb-conda default "

echo "hostname:"
hostname -f

tar -xf grid-source.tar

for $lfn in "[[LFNS]]"; do
    f=$(basename $lfn)
    lfn="${lfn:1}"
    echo "Move $f to $lfn ..."
    mv $f $lfn
done

$ENV_PREFIX {exec_job}
echo $?
