#!/bin/bash
set -e


error() {
    echo -e "\e[31mERROR:\e[0m $1" >&2
    exit 1
}

echo "Checking prerequisites..."
for cmd in git python3; do
    command -v $cmd &>/dev/null || error "$cmd is not installed. Please install it before continuing."
done


REPO="https://github.com/NextronSystems/thor-ts-mapper.git"
REPO_DIR="thor-ts-mapper" # need to change to nextron project name
VENV_NAME="venv-thor2ts"


if [ -f "setup.py" ]; then
    echo "Already inside the repository. Skipping clone."
else
    if [ -d "$REPO_DIR" ]; then
        echo "Repository already exists. Updating..."
        (cd "$REPO_DIR" && git pull) || error "Failed to update repository"
    else
        echo "Cloning TS-THOR repository..."
        git clone "$REPO" || error "Failed to clone repository"
    fi
    cd "$REPO_DIR" || error "Failed to enter repository directory"
fi



if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_NAME" || error "Failed to create virtual environment"
fi

echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate" || error "Failed to activate virtual environment"


echo "Installing thor_ts_mapper..."
pip install --upgrade pip || error "Failed to upgrade pip"
pip install -e . || error "Failed to install package"


echo "Testing installation..."
thor2ts --version || error "Installation test failed"

echo -e "\e[32mInstallation complete!\e[0m"
echo "Use 'thor2ts --help' for usage information."
echo "To use thor2ts in the future, activate the virtual environment first:"
echo "  source $PWD/$VENV_NAME/bin/activate"

set +e