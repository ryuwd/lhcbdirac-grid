# LHCb DIRAC Grid

This profile configures Snakemake to run on the LHCb DIRAC grid.

N.B. this is under development and doesn't actually work yet.

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

To deploy this profile, login to your grid UI and run

    mkdir -p ~/.config/snakemake
    cd ~/.config/snakemake
    cookiecutter https://github.com/ryuwd/lhcbdirac-grid.git

When asked for the storage path, insert whatever shall be the place where your data analysis results shall be stored. It must be a path that you can write to, on EOS. e.g. `root://eoslhcb.cern.ch//eos/lhcb/user/...`.

### Run workflow
Then, you can run Snakemake with
```
snakemake --profile lhcbdirac-grid ...
```

If a job fails, you will find the "external jobid" in the Snakemake error message.