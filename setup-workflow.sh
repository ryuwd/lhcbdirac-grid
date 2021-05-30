#!/bin/bash

USERNAME=$(whoami)

echo "Please enter below a unique name for this Snakemake workflow."
echo "This will determine where your inputs and outputs are kept on grid storage."
echo ""
read -p 'Workflow Name (must be unique): ' WORKFLOW_NAME

GRID_STORAGE_PREFIX="lhcb/user/${USERNAME:0:1}/${USERNAME}/snakemake-workflows/$WORKFLOW_NAME/"

echo ""
echo "Grid storage prefix has been determined as: "
echo "    LFN:/$GRID_STORAGE_PREFIX"
echo ""
echo "Is this OK? [y/n]" #TODO y/n prompt

echo ""

# Install Snakemake-Profile
echo "Install Snakemake-Profile for this workflow. "
(
    mkdir -p $HOME/.config/snakemake
    cd $HOME/.config/snakemake/
    cookiecutter https://github.com/ryuwd/lhcbdirac-grid.git workflow_name="$WORKFLOW_NAME" grid_storage_prefix="$GRID_STORAGE_PREFIX"
)


# Install Mambaforge.

if [ ! -d "$PWD/.mambaforge" ]; then
    echo "Installing mambaforge in $PWD/.mambaforge"

    curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh

    bash Mambaforge-Linux-x86_64.sh -b -p $PWD/.mambaforge
    rm Mambaforge-Linux-x86_64.sh

    # Activate the environment manually the first time
    eval "$(".mambaforge/bin/conda" shell.bash hook)"
    # Make it so that conda doesn't automatically activate the base environment
    conda config --set auto_activate_base false
else 
    # Activate the environment manually the first time
    eval "$(".mambaforge/bin/conda" shell.bash hook)"
fi 


echo "Install conda-pack."
mamba install -c conda-forge -y conda-pack

echo "Create snakemake environment."
mamba create -y -p .snakemake-grid -c conda-forge -c bioconda python=3.9 snakemake xrootd

echo "Install DiracSE patches."
(
    cd .snakemake-grid/lib/python3.9/site-packages/snakemake/remote/
    curl -L -O https://raw.githubusercontent.com/ryuwd/snakemake/roneil/DiracRemote/snakemake/remote/DiracSE.py
) &
(
    cd .snakemake-grid/lib/python3.9/site-packages/snakemake/
    curl -L -O https://raw.githubusercontent.com/ryuwd/snakemake/roneil/DiracRemote/snakemake/__init__.py
) &
wait;

echo "Packing relocatable environment. This can take a while."
conda pack -p .snakemake-grid --format tar --output snakemake-grid.tar

rm -rf .snakemake-grid

echo "Setup run-grid script."
cp $HOME/.config/snakemake/lhcbdirac-grid-$WORKFLOW_NAME/run-grid .
chmod +x run-grid


echo "To run this snakemake workflow on the Grid, please run the script ./run-grid -j <NJOBS> [other snakemake parameters]"

echo "Some tips for a smooth run: "
echo "   - *ALWAYS* use git version control. Ensure all files are tracked and changes committed."
echo "   - Group small jobs together: https://snakemake.readthedocs.io/en/stable/executing/grouping.html"
echo "   - Don't use directory inputs / outputs." #FIXME
echo "   - Upload any large input files to your grid storage prefix. Don't commit them to version control."
echo "         - If any input files are already on grid storage, specify the LFNs in your input data as a "
echo "           DiracSE remote file and they will be downloaded into the job."
echo "         - Alternatively, you can fix the Destination resource parameter e.g. to LCG.CERN.cern, and "
echo "           use a PFN. e.g. root:// url with XRootD remote file."
echo "   - pre-create and upload your conda environments, if you have any:"
echo "         $ touch .use-conda"
echo "     'run-grid' will make sure all conda environments are created, and then uploaded to the grid."
