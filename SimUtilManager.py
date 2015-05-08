import os
import re
import sys
import unittest
import subprocess
from SimctlWrapper import SimctlWrapper

class SimutilManager(object):
    """docstring for SimutilManager"""
    def __init__(self):
        super(SimutilManager, self).__init__()
        self.simStatus = None
        self.simctl = SimctlWrapper()
        self.simulatorPath = '/Applications/Xcode.app/Contents/Developer/Applications/iOS\ Simulator.app/Contents/MacOS/iOS\ Simulator'
    
    def showRuntime(self, status):
        print "== Runtime =="
        for x in status['Runtimes']:
            print "    Name: {name:<20}Id: {id:<56}Build: {build}".format(name=x['name'],id=x['id'],build=x['build'])

    def showDeviceTypes(self, status):
        print "== Device Types =="
        for x in status['DeviceTypes']:
            print "    Name: {name:<20}Id: {id}".format(name=x['name'],id=x['id'])

    def showDevices(self, status, showAll = False):
        print "== Devices =="
        for x in status['Devices']:
            if x['available'] or showAll:
                print "-- {runtime} --".format(runtime=x['runtime'])
                for d in x['devices']:
                    print "    Name: {name:<20}Id: {id:<40} Status: {state}".format(name=d['name'],id=d['id'], state=d['state'])
        

    def ShowSimulatorStatus(self):
        simStatus = self.simctl.GetStatus()
        self.showRuntime(simStatus)
        self.showDeviceTypes(simStatus)
        self.showDevices(simStatus,False)
        self.simStatus = simStatus

    def CreateSimulatorDevice(self, name, devicetype, runtime):
        newId = self.simctl.CreateDevice(name, devicetype, runtime)
        if newId:
            print "== Create Device =="
            print "    Name: {name:<20}Id: {id}".format(name=name,id=newId)
            self.simStatus = self.simctl.GetStatus()
        return newId

    def DeleteSimulatorDevice(self, ID):
        if not self.simStatus:
            sefl.simStatus = self.simctl.GetStatus()
        self.simctl.DeleteDevice(ID)
        print "== Delete Device =="

    def launchSimulatroByDevice(self, device):
        print "== Launch Simulator =="

        if device['state'] == 'Shutdown':
            print "    Name: {name:<20}Id: {id}".format(name=device['name'],id=device['id'])
            cmd = self.simulatorPath + " -CurrentDeviceUDID {id} &".format(id=device['id'])
            proc = subprocess.Popen(cmd,shell=True)
            print "    PID: %d" % proc.pid
            return proc.pid
        else:
            raise RuntimeError('Err: Device had been booted')


    def LaunchSimulatorById(self, deviceId):
        simStatus = self.simctl.GetStatus()
        if not simStatus:
            raise RuntimeError('Err: Can not get simctl status')

        device = self.simctl.getDeviceById(simStatus,deviceId)
        if not device:
            raise RuntimeError('Err: No such device id')

        self.launchSimulatroByDevice(device)


    def LaunchSimulatorByName(self, name, runtimeName):
        simStatus = self.simctl.GetStatus()
        if not simStatus:
            raise RuntimeError('Err: Can not get simctl status')

        device = self.simctl.getDeviceByName(simStatus,runtimeName,name)
        if not device:
            raise RuntimeError('Err: No such device name')

        self.launchSimulatroByDevice(device)

    def InstallApp(self, appPath='', deviceName='', runtimeName=''):
        pass


class TestSimUtilManager(unittest.TestCase):
    def test_ShowSimulatorStatus(self):
        simmgr = SimutilManager()
        simmgr.ShowSimulatorStatus()
        pass

    def test_CreateDeleteDevice(self):
        simmgr = SimutilManager()
        newId = simmgr.CreateSimulatorDevice("Unittest","iPhone 6","iOS 8.3")
        simmgr.DeleteSimulatorDevice(newId)

    def test_LaunchSimulator(self):
        simmgr = SimutilManager()
        try:
            simmgr.LaunchSimulatorByName("Debug2","iOS 8.3")
            simmgr.LaunchSimulatorByName("Debug","iOS 8.3")
        except Exception, e:
            print e

    def test_InstallApp(self):
        simmgr = SimutilManager()
        

if __name__ == '__main__':
    unittest.main()
