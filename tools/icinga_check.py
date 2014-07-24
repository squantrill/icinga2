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

# global
nobinary = [""]

# Script Configuration

critical_services = ["icinga2"]
apache_binarys = ['httpd', 'apache2', 'httpd2']
db_binarys = ["mysql", "postmaster"]
non_critical_service = ["snmptt", "npcd"]

# TODO - Add custom_paths to which()
custom_paths =[""]

# Script Functions

#Status Color
def get_distri():
    os_name = os.name
    return os_name

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
                print bcolors.OK, service, "- binary found"
                break
        else:
            print bcolors.CRIT, service, "- no binary found"

def service_status(service):
    exe_status = run_cmd("ps","cax")
    if service in exe_status:
        print  bcolors.OK, service, "- is running."
        return True
    else:
        print bcolors.CRIT, service, "- not running"
        return False

def service_check(service):
    exe_path = which(service)
    exe_status = run_cmd("ps","cax")
    if exe_path:
        for s in exe_path:
            if re.search(service, s) is not None:
                if service in exe_status:
                    if service == "postmaster":
                        print bcolors.OK, "postgresql - is running"
                        return
                    print bcolors.OK, service, "- is running"
                    return
                else:
                    if service == "postmaster":
                        print bcolors.CRIT, "postgresql - not running"
                        return
                    print bcolors.CRIT, service, "- not running"
                    return
    print bcolors.WARN, service,  "- no binary found"

    # if none of the provide Binarys where found
    if "no_sql" in nobinary:
        print bcolors.WARN,  "No SQL Binary Found.", db_binarys

    if "no_apache" in nobinary:
        print bcolors.WARN,  "No HTTP Binary Found.", apache_binarys

for i in apache_binarys:
    apache_bin = which(i)
    if apache_bin:
        critical_services.append(i)
    else:
        nobinary.append("no_apache")


for i in db_binarys:
    db_bin = which(i)
    if db_bin:
        critical_services.append(i)
    else:
        nobinary.append("no_sql")

# Script Config
# Color for Status / no Color on NT
if get_distri() == "nt":
    class bcolors:
        OK = ''
        WARN = ''
        CRIT = ''
else:
    class bcolors:
        OK = '\033[92m [OK] \033[0m'
        WARN = '\033[93m [WARN] \033[0m'
        CRIT = '\033[91m [CRIT] \033[0m'

# ICINGA CHECKS
def check_crit_services():
    for i in critical_services:
        service_check(i)

# MAIN
def main():
    check_crit_services()

if __name__ == "__main__":
    main()
