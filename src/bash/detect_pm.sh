#!/bin/bash

# Detect package manager from /etc/issue
function _found_pm {
  local _pmtype="$1"
  shift
  grep -qis "$*" /etc/issue && _PM="$_pmtype"
}

# Detect package manager
function PM_detect {
  _found_pm "pacman"      "Arch Linux"
  _found_pm "apt-get"     "Debian GNU/Linux"
  _found_pm "apt-get"     "Ubuntu"
  _found_pm "yum"         "CentOS"
  _found_pm "yum"         "Red Hat"
  _found_pm "yum"         "Fedora"
  _found_pm "zypper"      "SUSE"

  if [[ -z "$_PM" ]]; then
      # Fallback to shittier method

      if [[ -x "/usr/bin/pacman" ]]; then
        _PM='pacman'
      fi

      if [[ -x "/usr/bin/apt-get" ]]; then
        _PM='apt-get'
      fi

      if [[ -x "/usr/bin/yum" ]]; then
        _PM='yum'
      fi

      if [[ -x "/usr/bin/zypper" ]]; then
        _PM='zypper'
      fi

      if command -v brew >/dev/null; then
        _PM='brew'
      fi

      if [[ -z "$_PM" ]]; then
        _error "No supported package manager installed on system"
        _error "(supported: apt-get, brew, pacman, zypper, yum)"
        exit 1
      fi
  fi

  echo "$_PM"
}

PM_detect