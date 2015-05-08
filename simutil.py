import os
import re
import sys
import argparse
import unittest
from SimutilManager import SimutilManager

def parse_args():
    optParser = argparse.ArgumentParser(description='Utility to cotrol iOS Simulator.')
    optParser.add_argument('-l', '--list', dest='list', action='store_true', default=False, 
                            help='Show the status of iOS Simulator.')
    optParser.add_argument('-c', '--create', dest='create', action='store', default=None, type=str, metavar='DeviceName', 
                            help='Create new device of iOS Simulator.')
    optParser.add_argument('-d', '--delete', dest='delete', action='store', default=None, type=str, metavar='DeviceID', 
                            help='Delete device of iOS Simulator.')
    optParser.add_argument('--launch',dest='launch', action='store', default=None, type=str, metavar='DeviceName', 
                            help='Launch iOS Simulator with selected device.')
    return optParser.parse_args()

def main():
    try:
        args = parse_args()

        simmgr = SimutilManager()

        if args.list:
            simmgr.ShowSimulatorStatus()
        if args.create:
            simmgr.CreateSimulatorDevice(args.create,"iPhone 5","iOS 8.3")
        if args.delete:
            simmgr.DeleteSimulatorDevice(args.delete)
        if args.launch:
            simmgr.LaunchSimulatorByName(args.launch,"iOS 8.3")

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
