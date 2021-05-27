# LHCb DIRAC Grid

This profile configures Snakemake to run on the LHCb DIRAC grid.

N.B. this is under development and doesn't actually work yet.

## What works and what does not?

So far:

- Job submission
- Job status monitoring

Not so far:

- How do we deal with uploading input and output files to DIRAC storage, especially via snakemake's "remote files" mechanism?
    - can we use `eoslhcb.cern.ch` XRootD backed storage?
        - a lot simpler
        - does this only work on CERN nodes? Is it possible to use xrdcp directly to/from `eoslhcb.cern.ch` on those nodes?
        - this would be limiting in that jobs could only run at CERN

    - should a new `RemoteProvider` be created to upload and download files from SEs when not running in a grid job?

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

