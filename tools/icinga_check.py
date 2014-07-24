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

# Script Configuration

critical_services = ["icinga2"]
apache_binarys = ['httpd', 'apache2', 'httpd2']
db_binarys = ["mysql", "postmaster"]
non_critical_service = ["snmptt", "npcd"]

# TODO - Add custom_paths to which()
custom_paths =['']

# Script Functions
# TODO - Dont use Colors on NT
class bcolors:
    OK = '\033[92m [OK] \033[0m'
    WARN = '\033[93m [WARN] \033[0m'
    CRIT = '\033[91m [CRIT] \033[0m'

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

def find_apache_binary(services):
    apache_bin = which(services)
    if apache_bin:
        critical_services.append(services)

def find_db_binary(dbserver):
    db_bin = which(dbserver)
    if db_bin:
        critical_services.append(dbserver)

# Script Config
for i in apache_binarys:
    find_apache_binary(i)

for db in db_binarys:
    find_db_binary(db)

# ICINGA CHECKS
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
