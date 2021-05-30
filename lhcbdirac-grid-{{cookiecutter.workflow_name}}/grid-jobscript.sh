#!/bin/bash
# properties = {properties}

set -e

user=$2

source /cvmfs/lhcb.cern.ch/lib/LbEnv

cat pool_xml_catalog.xml

echo "hostname:"
hostname -f
ls -lah
echo "tar -xf snakemake-grid.tar"
tar -xf snakemake-grid.tar
echo "tar -xf grid-source.tar"
(
    mkdir conda-env && cd conda-env
    tar -xf grid-source.tar
)

for lfn in "[[LFNS]]"; do
    f=$(basename $lfn)
    lfn="${{lfn:1}}"
    echo "Move $f to $lfn ..."
    mkdir -p $(dirname $lfn)
    mv $f $lfn
done

source conda-env/bin/activate

{exec_job}
echo $?
