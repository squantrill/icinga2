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
#Status Color Class
class Notification:
    __colored = True
    def __init__(self):
        self.__colored = False if get_os() is "nt" else True
    def green(self, txt):
        return '\033[92m%s \033[0m' % txt
    def blue(self, txt):
        return '\033[94m%s \033[0m' % txt
    def yellow(self, txt):
        return '\033[93m%s \033[0m' % txt
    def red(self, txt):
        return '\033[91m%s \033[0m' % txt
    def ok(self, service, msg=" - is running"):
        state = ["[OK]", self.green]
        self.__print(state, service, msg)
    def warn(self, service, msg=" - binary not found"):
        state = ["[WARN]", self.yellow]
        self.__print(state, service, msg)
    def crit(self, service, msg=" - is not running"):
        state = ["[CRIT]", self.red]
        self.__print(state, service, msg)
    def __print(self, state, service, msg):
        print "%s %s %s" % (
            state[0] if self.__colored is False else state[1](state[0]),
            service,
            msg)

def get_os():
        os_name = os.name
        return os_name

def get_distri():
    if which("lsb_release"):
        get_lsb = run_cmd("lsb_release", "-d")
        os_info = re.search("Description:\s+(.+)", get_lsb)
        print "OS:", os_info.group(1)
    else:
        print os.name

def run_cmd_long(cmd, a="arg1", b="arg2", c="arg3"):
    p = subprocess.Popen([cmd, a, b, c], stdout=subprocess.PIPE)
    cmdout, err = p.communicate()
    return cmdout

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
    notify = Notification()
    exe_path = which(service)
    service_status(service)
    if which != None:
        for s in exe_path:
            if re.search(service, s) != None:
                notify.ok(service, "- binary found")
                break
        else:
            notify.warn(service, "- no binary found")

def service_status(service):
    notify = Notification()
    exe_status = run_cmd("ps","cax")
    if service in exe_status:
        notify.ok(service)
        return True
    else:
        notify.crit(service)
        return False

def service_check(service):
    notify = Notification()
    exe_path = which(service)
    exe_status = run_cmd("ps","cax")
    if exe_path:
        for s in exe_path:
            if re.search(service, s) is not None:
                if service in exe_status:
                    if service == "postmaster":
                        notify.ok("postgresql")
                        return
                    notify.ok(service)
                    return
                else:
                    if service == "postmaster":
                        notify.crit("postgresql")
                        return
                    notify.crit(service)
                    return
    notify.warn(service)
    # if none of the provide Binarys where found
    if "no_sql" in nobinary:
        notify.warn("No SQL Binary Found.", db_binarys)

    if "no_apache" in nobinary:
        notify.warn("No HTTP Binary Found.", apache_binarys)


# Script Config
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

# ICINGA CHECKS
def check_crit_services():
    for i in critical_services:
        service_check(i)

# MAIN
def main():
    notify = Notification()
    print "##############################################################################"
    print "#################     Icinga2 Check and Reporting Script     #################"
    print "#################    Franz Holzer / Team Quality Assurance   #################"
    print "##############################################################################"
    print notify.blue("System Information:")
    get_distri()

    print notify.blue("Critical Service Checks:")
    check_crit_services()

if __name__ == "__main__":
    main()
