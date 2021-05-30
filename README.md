# LHCbDIRAC Grid Snakemake Profile

This profile configures Snakemake to run on the LHCb DIRAC grid.

N.B. this is under development and doesn't actually work yet.

## What works and what does not?

So far:

- Job submission
- Job status monitoring

In progress:

- How do we deal with uploading input and output files to DIRAC storage, especially via snakemake's "remote files" mechanism?
    - I created https://github.com/ryuwd/snakemake/compare/main...ryuwd:roneil/DiracRemote to support upload / download
        of files with `lb-dirac` to/from CERN-USER storage (if uploading) or any SE if downloading. Upload / download works fine.
    - Job submission script will ensure input files are downloaded by their LFNs into the job sandbox. Job script moves input file to a
        location where `snakemake` picks it up.
    - Snakemake is LFN-aware and uploads the file from the sandbox to grid storage at the end of the job.

- Conda environments with `--use-conda`.


- Automatic setup with `setup-workflow.sh`


## Setup

### Prerequisites

#### Setup workflow submission environment

Log in to CERN lxplus.

Setup `lb-conda default`

```
lb-conda default
```

Setup a grid proxy
```
lhcb-proxy-init
```

### Deploy profile

To deploy this profile,
```
    mkdir -p ~/.config/snakemake
    cd ~/.config/snakemake
    cookiecutter https://github.com/ryuwd/lhcbdirac-grid.git
```

When asked for the storage path, insert whatever shall be the place where your data analysis results shall be stored. It must be a path that you can write to, on EOS. e.g. `eoslhcb.cern.ch//eos/lhcb/user/...`.

If you have multiple workflows, please be mindful that you use a different storage path / prefix to avoid clashing filenames.

### Run workflow
Then, you can run Snakemake with
```
snakemake --profile lhcbdirac-grid ...
```

If a job fails, you will find the "external jobid" in the Snakemake error message.

