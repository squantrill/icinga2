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
import platform
import locale
import math
from itertools import islice

#global
script_warning = []

# Script Configuration
critical_services = ["icinga2"]
apache_binarys = ['httpd', 'apache2', 'httpd2']
db_binarys = ["mysql", "postmaster"]
non_critical_services = ["snmptt", "npcd"]
#the "real" non Critical Services List
non_crit_services = []

#Icinga2 Directory
icinga2_locations = ["/etc/icinga2", "/opt/icinga2/etc", "/usr/local/icinga2/etc"]

# TODO - Add custom_paths to which()
custom_paths =[""]

# Script Functions
class Notification:
    __colored = True
    def __init__(self):
        if get_os() is "nt":
            self.__colored = ""
        else:
            self.__colored = "color"
    def green(self, txt):
        return self.__color('\033[92m%s\033[0m', txt)
    def yellow(self, txt):
        return self.__color('\033[93m%s\033[0m', txt)
    def blue(self, txt):
        return self.__color('\033[94m%s\033[0m', txt)
    def underline(self, txt):
        return self.__color('\033[4m%s\033[0m', txt)
    def bold(self, txt):
        return self.__color('\033[1m%s\033[0m', txt)
    def red(self, txt):
        return self.__color('\033[91m%s\033[0m', txt)
    def darkcyan(self, txt):
        return self.__color('\033[36m%s\033[0m', txt)
    def ok(self, service, msg=" - is running"):
        self.__print(self.green("[OK]"), service, msg)
    def warn(self, service, msg=" - no binary found"):
        self.__print(self.yellow("[WARN]"), service, msg)
    def crit(self, service, msg=" - is not running"):
        self.__print(self.red("[CRIT]"), service, msg)
    def __color(self, color, text):
        if self.__colored:
            return color % text
        else:
            return text
    def __print(self, state, service, msg):
        print "%s %s %s" % (state, service, msg)

def slurp(input_file):
    x = open(input_file)
    try:
       output = x.read()
       return chomp(output)
    finally:
        x.close()

def per_line(lis, n):
    it = iter(lis)
    le = float(len(lis))
    for _ in xrange(int(math.ceil(le/n))):
        yield ", ".join(islice(it, n))

def chomp(s):
    if s:
        return s.rstrip('\n')
    else:
        return

def get_os():
        os_name = os.name
        return os_name

def query_pgsql(select_string):
    output = get_icingafile_output("/features-available/ido-pgsql.conf")
    pgsql_data = re.search("\"ido-pgsql\".+user.+\"(?P<user>.+)\".+password.+\"(?P<password>.+)\".+host.+\"(?P<host>.+)\".+database.+\"(?P<database>.+)\"", output, re.S)
    os.environ['PGPASSWORD'] = pgsql_data.group("password")
    sql_check = subprocess.Popen(['psql', '-U', pgsql_data.group("user"), '-d', pgsql_data.group("database"), '-h', pgsql_data.group("host"), '-w' , '-c', select_string], stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    sqlout = sql_check.communicate()[0]
    return sqlout

def query_mysql(select_string):
    output = get_icingafile_output("/features-available/ido-mysql.conf")
    mysql_data = re.search("\"ido-mysql\".+user.+\"(?P<user>.+)\".+password.+\"(?P<password>.+)\".+host.+\"(?P<host>.+)\".+database.+\"(?P<database>.+)\"", output, re.S)
    sql_check = subprocess.Popen(['mysql', '-u', mysql_data.group("user"), '--password='+mysql_data.group("password"),'--database='+mysql_data.group("database"), '--execute='+select_string], stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    sqlout = sql_check.communicate()[0]
    return sqlout

def run_check(check, a="check_argument", b="value", c="", d=""):
    p = subprocess.Popen(["sudo", "-u", "icinga", check, a, b, c, d], stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    cmdout, err = p.communicate()
    return cmdout

def run_cmd(cmd, a=""):
    p = subprocess.Popen([cmd, a], stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
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

# TODO - No checks tested if Postgres AND Mysql is installed and used at once
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

# Script Config
def find_apache_bin():
    global script_warning
    for i in apache_binarys:
        apache_bin = which(i)
        if apache_bin:
            critical_services.append(i)
            return
    script_warning.extend(["No Apache Binary found:",apache_binarys, "\n"])

def find_sql_bin():
    global script_warning
    for i in db_binarys:
        db_bin = which(i)
        if db_bin:
            critical_services.append(i)
            return
    script_warning.extend(["No SQL Binary found:", db_binarys, "\n"])

def find_non_crit_service_bin():
    global script_warning
    for i in non_critical_services:
        non_crit_serv = which(i)
        if non_crit_serv:
            non_crit_services.append(i)
            return
    script_warning.extend(["No non-critical Service Binary found:",non_critical_services, "\n"])

def get_icinga2_dir():
    for l in icinga2_locations:
        if os.path.isfile("%s/icinga2.conf" % l):
               return l
    script_warning.extend(["No Icinga2 Directory found:",icinga2_locations, "\n"])

#CHECKS
def get_distri():
    if which("lsb_releasee"):
        get_lsb = run_cmd("lsb_release", "-d")
        os_info = re.search("Description:\s+(.+)", get_lsb)
        print "OS:", os_info.group(1)
    elif os.path.isfile("/etc/redhat-release"):
        os_info = slurp("/etc/redhat-release")
        print "OS:", os_info
    elif os.path.isfile("/etc/debian_version"):
        os_info = slurp("/etc/debian_version")
        print "OS:", os_info
    elif which("ping.exe"):
        print "OS:", platform.platform()
    else:
        print "OS: unknown"
    if which("uname"):
        kernel = run_cmd("uname", "-rp")
        print "Kernel:", chomp(kernel)

def check_crit_services():
    for i in critical_services:
        service_check(i)

def check_non_critical_service():
    for i in non_crit_services:
        service_check(i)

def python_ver():
    py_ver = platform.python_version()
    print "Python Ver.:", py_ver

def php_ver():
    if which("php"):
        output = run_cmd("php", "-v")
        phpver = re.search("PHP.(\d.\d.\d)", output)
        print "PHP Ver.:", phpver.group(1)

def selinux():
    if which("selinuxenabled"):
        output = run_cmd("getenforce")
        print "Selinux Status:", chomp(output)

def get_locale():
    output = locale.getdefaultlocale()
    LANG = ','.join(output)
    print "LANG:", LANG

def apache_info():
    for i in apache_binarys:
        apache_path = which(i)
        if apache_path:
            apache_bin = i
            output = run_cmd(apache_bin, "-V")
            short = re.search(".erver..ersion:.(.+)", output)
            print "Apache Ver.:", short.group(1)

def sql_info():
    for i in db_binarys:
        sql_path = which(i)
        if sql_path:
            sql_bin = i
            output = run_cmd(sql_bin, "-V")
            print "DB Server Ver.:", chomp(output[:32])

def icinga_version():
    notify = Notification()
    if which("icinga2"):
        output = run_cmd("icinga2", "-V")
        icingaver = re.search(".+\(\w+..(.+).", output)
        print "Icinga Ver.:", icingaver.group(1)

def get_enabled_features():
    notify = Notification()
    if which("icinga2"):
        output = run_cmd("icinga2-enable-feature", "")
        enabled_f = re.search("\s+Enabled.features..(.+)", output)
        features = enabled_f.group(1).split(" ")
        print notify.underline("Enabled Features:")
        for feature in per_line(features, 4):
            print feature

def script_warnings():
    for i in script_warning:
        print i,

def get_icingafile_output(path_to_file):
    idir = get_icinga2_dir()
    if os.path.isfile("%s%s" % (idir, path_to_file)):
        output = slurp("%s%s" % (idir, path_to_file))
        return output

def get_plugin_path():
    output = get_icingafile_output("/constants.conf")
    if output:
        path = re.search("const.+PluginDir.+\"(.+)\"", output)
        return path.group(1)

def check_local_disk():
    notify = Notification()
    pluginpath = get_plugin_path()
    if pluginpath:
        output = run_check("%s/check_disk" % pluginpath, "-c", "5\%")
        if "OK" in output:
            notify.ok("check_disk -c 5%:", output[:32])
        elif "CRIT" in output:
            notify.warn("check_disk -c 5%:", output[:44])
        else:
            notify.crit("check_disk -c 5%:", "Cant run check_disk with user \"icinga\"")

#TODO better if condition (postmaster, mysql)
def check_programstatus():
    notify = Notification()
    if "postmaster" in critical_services:
        select_string = "SELECT ps.status_update_time FROM icinga_programstatus AS ps\
                            JOIN icinga_instances AS i ON ps.instance_id=i.instance_id\
                            WHERE ((SELECT extract(epoch from status_update_time) FROM icinga_programstatus) > (SELECT extract(epoch from now())-60))\
                            AND i.instance_name='default'"
        pstatus = query_pgsql(select_string)
        if pstatus:
            date = re.search("\s+status_update_time\s+.+\s+(\d.+)", pstatus)
            if date:
                notify.ok("IDO Programstatus:", date.group(1))
            else:
                notify.crit("IDO Programstatus:", "No Status Time")
        else:
            notify.warn("IDO Programstatus:","Error - check postgresql status")

    elif "mysql" in critical_services:
        select_string = "SELECT status_update_time FROM icinga_programstatus ps\
                            JOIN icinga_instances i ON ps.instance_id=i.instance_id\
                            WHERE (UNIX_TIMESTAMP(ps.status_update_time) > UNIX_TIMESTAMP(NOW())-60)\
                            AND i.instance_name='default'"
        mstatus = query_mysql(select_string)
        if mstatus:
            date = re.search(".*status_update_time.*(\d{4}.{15})", mstatus, re.S)
            if date:
                notify.ok("IDO Programstatus:", date.group(1))
            else:
                notify.crit("IDO Programstatus:", "No Status Time")
        else:
            notify.warn("IDO Programstatus:","Error - check mysql status")

def pre_script_config():
    get_icinga2_dir()
    find_non_crit_service_bin()
    find_sql_bin()
    find_apache_bin()

# MAIN Output
def main():
    pre_script_config()
    notify = Notification()
    print "===================================================================="
    print "Icinga2 Verify Script:"
    print "===================================================================="
    print notify.blue("Script Warnings:")
    script_warnings()
    print ""
    print notify.blue("System Information:")
    get_distri()
    selinux()
    get_locale()
    print ""
    python_ver()
    php_ver()
    apache_info()
    sql_info()
    print ""
    print notify.blue("Icinga Checks:")
    #info
    icinga_version()
    get_enabled_features()
    print ""
    #checks
    check_programstatus()
    check_local_disk()
    print ""
    print notify.blue("Essential Service Checks:")
    check_crit_services()
    print ""
    print notify.blue("non-critical Service Checks:")
    check_non_critical_service()
    print "===================================================================="
if __name__ == "__main__":
    main()
