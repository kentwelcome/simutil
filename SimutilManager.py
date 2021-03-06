import os
import re
import sys
import unittest
import subprocess
import plistlib
import time
import datetime
from bplist import BPlistReader
from SimctlWrapper import SimctlWrapper


class SimutilManager(object):
    """docstring for SimutilManager"""
    def __init__(self):
        super(SimutilManager, self).__init__()
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

    def GetDeviceStatus(self, deviceName, deviceRuntime):
        simStatus = self.simctl.GetStatus()
        device = self.simctl.getDeviceByName(simStatus, deviceName,deviceRuntime)
        return device

    def CreateSimulatorDevice(self, deviceName, typeName, runtimeName):
        device = self.GetDeviceStatus(deviceName,runtimeName)
        print "== Create Device =="
        if device:
            print "    Device had been created!"
        newId = self.simctl.CreateDevice(deviceName, typeName, runtimeName)
        if newId:
            print "    Name: {name:<20}Id: {id}".format(name=deviceName,id=newId)
        return newId

    def DeleteSimulatorDevice(self, deviceName, deviceRuntime):
        device = self.GetDeviceStatus(deviceName,deviceRuntime)
        if not device:
            raise RuntimeError('Err: No such device')
        if device['state'] == 'Booted':
            raise RuntimeError('Err: Device is still running')

        print "== Delete Device =="
        print "    Name: {name:<20}Id: {id}".format(name=device['name'],id=device['id'])
        self.simctl.DeleteDevice(device['id'])
        pass

    def DeleteSimulatorDeviceById(self, ID):
        simStatus = self.simctl.GetStatus()
        device = self.simctl.getDeviceById(simStatus, ID)
        if not device:
            raise RuntimeError('Err: No such device id')
        if device['state'] == 'Booted':
            raise RuntimeError('Err: Device is still running')

        print "== Delete Device =="
        print "    Name: {name:<20}Id: {id}".format(name=device['name'],id=device['id'])
        self.simctl.DeleteDevice(ID)
        
    def launchSimulatroByDevice(self, device):
        print "== Launch Simulator =="
        print "    Name: {name:<20}Id: {id}".format(name=device['name'],id=device['id'])
        if device['state'] == 'Shutdown':
            print "    Status: Booting..."
            cmd = self.simulatorPath + " -CurrentDeviceUDID {id} &".format(id=device['id'])
            proc = subprocess.Popen(cmd,shell=True)
            print "    PID: %d" % proc.pid
            return proc.pid
        else:
            print "    Status: Booted"
            return None


    def LaunchSimulatorById(self, deviceId):
        simStatus = self.simctl.GetStatus()
        device = self.simctl.getDeviceById(simStatus,deviceId)
        if not device:
            raise RuntimeError('Err: No such device id')
        return self.launchSimulatroByDevice(device)


    def LaunchSimulatorByName(self, deviceName, runtimeName):
        simStatus = self.simctl.GetStatus()
        device = self.simctl.getDeviceByName(simStatus,deviceName,runtimeName)
        if not device:
            raise RuntimeError('Err: No such device name')
        return self.launchSimulatroByDevice(device)

    def generateMovName(self, device):
        ts = time.time()
        st = st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')
        moviePath = "./Task/{deviceName}_{st}.mov".format(deviceName=device['name'],st=st)
        return moviePath

    def RecordSimulator(self, device):
        if device['state'] != 'Booted':
            raise RuntimeError('Err: Simulator should be booted')
        
        moviePath = self.generateMovName(device)

        print "== Start Record =="
        print "    Record File: {moviePath}".format(moviePath=moviePath)
        cmd = "./bin/SimulatorMonitor {deviceName} {moviePath}".format(deviceName=device['name'],moviePath=moviePath)
        os.system(cmd)
        print "== Stop Record =="

    def RecordSimulatorByName(self, deviceName, runtimeName):
        device = self.GetDeviceStatus(deviceName, runtimeName)
        if not device:
            raise RuntimeError('Err: No such device name')
        self.RecordSimulator(device)

    def extractBPlist(self, bplist):
        fd = open(bplist,'r')
        data = fd.read()
        bp = BPlistReader(data)
        return bp.parse()
    
    def getAppInfo(self, appPath):
        plistPath = os.path.join(appPath,'Info.plist')
        if os.path.isfile(plistPath):
            return self.extractBPlist(plistPath)
        else:
            return None

    def showAppInfo(self, app):
        print "-- App Info --"
        print "    App Name:            {name}".format(name=app['CFBundleName'])
        print "    App Identifier:      {AppId}".format(AppId=app['CFBundleIdentifier'])
        print "    Minimum Support OS:  {os}".format(os=app['MinimumOSVersion']) 
        print "    Platform Name:       {platform}".format(platform=app['DTPlatformName'])
        print "    SDK Name:            {SDK}".format(SDK=app['DTSDKName'])

    def InstalliOSApp(self, appPath, deviceName, runtimeName):
        simStatus = self.simctl.GetStatus()
        device = self.simctl.getDeviceByName(simStatus,deviceName,runtimeName)
        if not device:
            raise RuntimeError('Err: No such device name')
        if not os.path.isdir(appPath):
            raise RuntimeError('Err: No such App')
        if device['state'] != 'Booted':
            raise RuntimeError('Err: Simulator should be booted')
        
        app = self.getAppInfo(appPath)
        if not app:
            raise RuntimeError('Err: Invalid iOS App')

        print "== Install Appliction =="
        print "    App Path: {path}".format(path=appPath)
        self.showAppInfo(app)
        self.simctl.InstallApp(appPath,device)
        pass

    def UninstalliOSAppByPath(self, appPath, deviceName, runtimeName):
        app = self.getAppInfo(appPath)
        if not app:
            raise RuntimeError('Err: Invalid iOS App')

        device = self.GetDeviceStatus(deviceName,runtimeName)
        if not device:
            raise RuntimeError('Err: No such device name')

        if device['state'] != 'Booted':
            raise RuntimeError('Err: Simulator should be booted')

        print "== Uninstall Appliction by Path =="
        self.showAppInfo(app)
        self.simctl.UninstallApp(app['CFBundleIdentifier'],device)


    def UninstalliOSAppBy(self, appId, deviceName, runtimeName):
        simStatus = self.simctl.GetStatus()
        device = self.simctl.getDeviceByName(simStatus,runtimeName,deviceName)
        if not device:
            raise RuntimeError('Err: No such device name')
        if device['state'] != 'Booted':
            raise RuntimeError('Err: Simulator should be booted')
        print "== Uninstall Appliction =="
        print "    App Identifier: {id}".format(id=appId)
        self.simctl.UninstallApp(appId,device)
        pass

class TestSimUtilManager(unittest.TestCase):
    def setUp(self):
        print "Running:", self._testMethodName

    def test_ShowSimulatorStatus(self):
        simmgr = SimutilManager()
        simmgr.ShowSimulatorStatus()
        pass

    def test_CreateDeleteDevice(self):
        simmgr = SimutilManager()        
        newId = simmgr.CreateSimulatorDevice("Unittest","iPhone 6","iOS 8.3")
        simmgr.DeleteSimulatorDevice("Unittest","iOS 8.3")

    def test_LaunchSimulator(self):
        simmgr = SimutilManager()
        simmgr.LaunchSimulatorByName("Debug2","iOS 8.3")
        simmgr.LaunchSimulatorByName("Debug","iOS 8.3")

    def test_InstalliOSApp(self):
        simmgr = SimutilManager()
        simmgr.LaunchSimulatorByName("TestInstallApp","iOS 8.3")
        simmgr.InstalliOSApp('./TestApp/TestApp.app',"TestInstallApp","iOS 8.3")
        
    def test_UninstalliOSApp(self):
        simmgr = SimutilManager()
        try:
            simmgr.LaunchSimulatorByName("TestInstallApp","iOS 8.3")
            #simmgr.UninstalliOSApp('simutil.TestApp',"TestInstallApp","iOS 8.3")
        except Exception, e:
            print e
        

if __name__ == '__main__':
    unittest.main()
