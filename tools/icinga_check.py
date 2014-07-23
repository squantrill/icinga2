#! /usr/bin/python
#/******************************************************************************
# * Icinga 2                                                                   *
# * Copyright (C) 2012-2014 Icinga TEAM QS  (http://www.icinga.org)            *
# * Author: Franz Holzer                                                        *
# *                                                                            *
# * This program is free software; you can redistribute it and/or              *
# * modify it under the terms of the GNU General Public License                *
# * as published by the Free Software Foundation; either version 2             *
# * of the License, or (at your option) any later version.                     *
# *                                                                            *
# * This program is distributed in the hope that it will be useful,            *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of             *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
# * GNU General Public License for more details.                               *
# *                                                                            *
# * You should have received a copy of the GNU General Public License          *
# * along with this program; if not, write to the Free Software Foundation     *
# * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.             *
# *****************************************************************************/

import os
import sys
import subprocess
import re

# Global Variables
global critical_services
global non_critical_services

# Script Configuration
critical_services = ["httpd", "mysql", "postmaster", "icinga", "ido2db"]
non_critical_service = ["snmptt", "npcd"]

## apache 'httpd', 'apache2', 'httpd2'
# Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    CRIT = '\033[91m'
    ENDC = '\033[0m'

#Script Functions
def run_cmd(cmd, a="arg", b="service"):
    p = subprocess.Popen([cmd, a], stdout=subprocess.PIPE)
    cmdout, err = p.communicate()
    return cmdout

def which(name, flags=os.X_OK):
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result

def service_binary(service):
    exe_path = which(service)
    service_status(service)
    if which != None:
        for s in exe_path:
            if re.search(service, s) != None:
                print bcolors.OKGREEN + service + bcolors.ENDC, "- binary found"
                break
        else:
            print bcolors.CRIT + service + bcolors.ENDC, "- no binary found"

def service_status(service):
    exe_status = run_cmd("ps","cax")
    if service in exe_status:
        print  bcolors.OKGREEN + service + bcolors.ENDC, "- is running."
        return True
    else:
        print bcolors.CRIT + service + bcolors.ENDC, "- not running"
        return False

def service_check(service):
    exe_path = which(service)
    exe_status = run_cmd("ps","cax")
    if exe_path:
        for s in exe_path:
            if re.search(service, s) is not None:
                if service in exe_status:
                    print bcolors.OKGREEN + service + bcolors.ENDC, "- is running."
                    return
                else:
                    print bcolors.CRIT + service + bcolors.ENDC, "- not running"
                    return

    print service, "- no binary found"

# ICINGA CHECKS
# SERVICE CHECK - Test

def check_crit_services():
    for i in critical_services:
        service_check(i)

def get_distri():
    if os.name == 'nt':
        print "Operating System: %s" % os.name
        print "Windows Checks are not Tested!"

# MAIN
def main():
    get_distri()
    check_crit_services()

if __name__ == "__main__":
    main()
