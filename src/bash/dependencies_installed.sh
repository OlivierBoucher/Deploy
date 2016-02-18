#!/bin/bash

function _dpkg_is_installed {
    return $(dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -c "ok installed")
}

function _rpm_is_installed {
    return $(rpm -q "$1" &>/dev/null)
}

function _pacman_is_installed {
    return $(pacman -Q "$1" &>/dev/null)
}

function is_installed {
    if [ "$1" == "dpkg" ]; then
        return _dpkg_is_installed $2
    fi
}