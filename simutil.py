import os
import re
import sys
import argparse
import unittest
from SimutilOptParser import SimutilOptParser
from SimutilManager import SimutilManager

def main():
    args = SimutilOptParser(sys.argv).parse()

    simmgr = SimutilManager()

    if args.cmd == 'list':
        if not args.deviceName:
            simmgr.ShowSimulatorStatus()
        else:
            #TODO: Implement method ShowDeviceStatus in SimutilManager
            pass
    elif args.cmd == 'create':
        simmgr.CreateSimulatorDevice(args.deviceName, args.deviceType, args.runtimeName)
    elif args.cmd == 'delete':
        simmgr.DeleteSimulatorDevice(args.deviceName,args.runtimeName)
    elif args.cmd == 'launch':
        simmgr.LaunchSimulatorByName(args.deviceName,args.runtimeName)
    elif args.cmd == 'install':
        simmgr.InstalliOSApp(args.appPath,args.deviceName,args.runtimeName)
    elif args.cmd == 'uninstall':
        simmgr.UninstalliOSAppByPath(args.appPath,args.deviceName,args.runtimeName)
    else:
        print 'Unsupport command!'


if __name__ == '__main__':
    main()
