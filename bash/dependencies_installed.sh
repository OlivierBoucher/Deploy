#!/bin/bash

g_ret=1

function _dpkg_is_installed {
    dpkg-query -s "$1" | grep -q "install ok installed"
    g_ret=$?
}

function _rpm_is_installed {
    rpm -q "$1" &>/dev/null
    g_ret=$?
}

function _pacman_is_installed {
    pacman -Q "$1" &>/dev/null
    g_ret=$?
}

function is_installed {
    if [ "$1" == "apt-get" ]; then
        _dpkg_is_installed $2
    elif [ "$1" == "yum" ]; then
        _rpm_is_installed $2
    elif [ "$1" == "pacman" ]; then
        _pacman_is_installed $2
    fi

    echo "$g_ret"
}