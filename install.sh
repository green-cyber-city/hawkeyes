#!/bin/sh
# Hawkeyes installer — no Python or pip required.
# Installs a standalone `hawk` binary to ~/.local/bin (or a directory you choose).
#
# Usage:
#   curl -fsSL https://YOUR-HOST/install.sh | sh
#
# Optional environment variables:
#   HAWKEYES_VERSION=1.0.0
#   HAWKEYES_BASE_URL=https://YOUR-HOST/releases/v1.0.0
#   HAWKEYES_INSTALL_DIR=$HOME/.local/bin

set -e

VERSION="${HAWKEYES_VERSION:-1.0.0}"
BASE_URL="${HAWKEYES_BASE_URL:-https://github.com/kyawyelin284/tcp-port-scanner/releases/download/v${VERSION}}"
INSTALL_DIR="${HAWKEYES_INSTALL_DIR:-${HOME}/.local/bin}"

bold=""
reset=""
if [ -t 1 ]; then
    bold="\033[1m"
    reset="\033[0m"
fi

info()  { printf '%s\n' "$1"; }
fail()  { printf 'Error: %s\n' "$1" >&2; exit 1; }

detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"

    case "${OS}" in
        Linux) ;;
        *) fail "Unsupported operating system: ${OS}. Hawkeyes supports Linux only." ;;
    esac

    case "${ARCH}" in
        x86_64|amd64)  ARCH="x86_64" ;;
        aarch64|arm64) ARCH="aarch64" ;;
        *) fail "Unsupported CPU architecture: ${ARCH}" ;;
    esac

    BINARY_NAME="hawk-linux-${ARCH}"
}

download_binary() {
    URL="${BASE_URL}/${BINARY_NAME}"
    TMP="$(mktemp)"
    trap 'rm -f "$TMP"' EXIT INT HUP TERM

    info "Downloading Hawkeyes ${VERSION} for linux/${ARCH}..."
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$URL" -o "$TMP"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$TMP" "$URL"
    else
        fail "curl or wget is required to download Hawkeyes."
    fi

    chmod +x "$TMP"
    mkdir -p "$INSTALL_DIR"
    mv "$TMP" "${INSTALL_DIR}/hawk"
    trap - EXIT INT HUP TERM
}

verify_install() {
    if ! "${INSTALL_DIR}/hawk" --version >/dev/null 2>&1; then
        fail "Installed binary failed to run. Check your platform and download URL."
    fi
}

print_success() {
    printf '\n'
    info "${bold}Hawkeyes installed successfully.${reset}"
    info "  Binary: ${INSTALL_DIR}/hawk"
    info "  Version: $("${INSTALL_DIR}/hawk" --version 2>/dev/null || echo "${VERSION}")"
    printf '\n'

    case ":${PATH}:" in
        *":${INSTALL_DIR}:"*) ;;
        *)
            info "Add Hawkeyes to your PATH:"
            info "  export PATH=\"\${PATH}:${INSTALL_DIR}\""
            info "Add that line to ~/.bashrc or ~/.zshrc to keep it permanently."
            printf '\n'
            ;;
    esac

    info "Try it:"
    info "  hawk"
    info "  hawk target example.com --ports \"80,443\""
    printf '\n'
    info "Only scan systems you own or have permission to test."
}

main() {
    info ""
    info "${bold}HAWKEYES${reset} installer"
    info "Standalone TCP port scanner — no Python or pip needed."
    info ""

    detect_platform
    download_binary
    verify_install
    print_success
}

main "$@"
