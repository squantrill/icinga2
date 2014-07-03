import os
import sys
import logging
import argparse


# Commandline Parser
parser = argparse.ArgumentParser(description='icinga2_check helper')

parser.add_argument('--r', help='Shows the Verbose Reporting Output', required=False, action='store_true')
parser.add_argument('--s', help='Shows the Sanity Checks', required=False, action='store_true')
parser.add_argument('--i', help='Shows a Issue Tracker prepared Output', required=False, action='store_true')
args = parser.parse_args()

#Check if we are on Windows
os_check = os.name
if os_check == 'nt':
    print "Windows"
    sys.exit()






