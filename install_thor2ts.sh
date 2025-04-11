#!/bin/bash

RED="\e[31m"
GREEN="\e[32m"
NC="\e[0m"

error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
    return 1
}

info() {
    echo -e "${GREEN}$1${NC}"
}

install_thor2ts() {
    info "Checking prerequisites..."
    command -v python3 &>/dev/null || { error "python3 is not installed. Please install it before continuing."; return 1; }
    python3 -c "import venv" &>/dev/null || { error "Python venv module not available. Please install it (e.g., sudo apt install python3-venv)."; return 1; }

    VENV_NAME="venv-thor2ts"

    if [ ! -d "$VENV_NAME" ]; then
        info "Creating virtual environment..."
        python3 -m venv "$VENV_NAME" || { error "Failed to create virtual environment"; return 1; }
    fi

    info "Installing thor_ts_mapper..."
    source "$VENV_NAME/bin/activate" || { error "Failed to activate virtual environment"; return 1; }
    pip install . || { error "Failed to install thor_ts_mapper"; return 1; }

    command -v thor2ts &>/dev/null || { error "Installation failed: thor2ts command not found"; return 1; }
    info "Installation complete!"
}


if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    install_thor2ts && {
        info "Successfully installed thor_ts_mapper"
        info "Virtual environment is now active."
    }
else
    install_thor2ts && {
        info "Successfully installed thor_ts_mapper"
        echo ""
        info "To use thor2ts, you need to activate the environment with:"
        info "  source $VENV_NAME/bin/activate"
        echo ""
        info "For automatic activation, you can run:"
        info "  source $(basename "$0")"
    }
fi