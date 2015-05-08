import os
import re
import sys
import unittest
from SimctlListParser import SimctlListParser

class SimctlWrapper(object):
    """docstring for SimctlWrapper"""
    def __init__(self):
        super(SimctlWrapper, self).__init__()
        self.debug = False

    def SetDebug(self, val):
        if val == True:
            self.debug = True
        else:
            self.debug = False

    def GetStatus(self):
        simctlOutput = self.runSimctl("list")
        simctlParser = SimctlListParser(simctlOutput)
        if self.debug:
            simctlParser.SetDebug(True)
        return simctlParser.parse()

    def getRuntimeByName(self, status, runtimeName):
        for x in status['Runtimes']:
            if x['name'] == runtimeName:
                return x
        return None

    def getTypeByName(self, status, typeName):
        for x in status['DeviceTypes']:
            if x['name'] == typeName:
                return x
        return None

    def getDeviceByName(self, status, runtimeName, deviceName):
        for x in status['Devices']:
            if x['runtime'] == runtimeName:
                for d in x['devices']:
                    if d['name'] == deviceName:
                        return d
        return None

    def getDeviceById(self, status, deviceId):
        for x in status['Devices']:
            if x['available']:
                for d in x['devices']:
                    if d['id'] == deviceId:
                        return d
        return None

    def DeleteDevice(self, deviceId):
        status = self.GetStatus()
        device = self.getDeviceById(status,deviceId)

        if not device:
            raise RuntimeError('Err: No such device')

        deleteOption = "delete {deviceId}".format(deviceId=deviceId)
        self.runSimctl(deleteOption)

    def CreateDevice(self, name, deviceTypeName, runtimeName):
        status = self.GetStatus()
        deviceType = self.getTypeByName(status,deviceTypeName)
        runtime = self.getRuntimeByName(status,runtimeName)

        if (not deviceType) or (not runtime):
            raise RuntimeError('Err: Not such device/rutime')

        if self.getDeviceByName(status,runtimeName,name):
            raise RuntimeError('Err: Device had been create')

        createOption = "create {name} {typeid} {runtimeid}".format(name=name,typeid=deviceType['id'],runtimeid=runtime['id'])
        
        newId = self.runSimctl(createOption).replace('\n','')
        return newId

    def runSimctl(self,options):
        cmd = "xcrun simctl {option}".format(option=options)
        return os.popen(cmd).read()

class TestSimctlWrapper(unittest.TestCase):
    def test_ShowStatus(self):
        simctl = SimctlWrapper()
        simctl.SetDebug(False)
        simctl.GetStatus()
        pass
    def test_CreateAndDeleteNewDevice(self):
        simctl = SimctlWrapper()
        simctl.SetDebug(False)
        try:
            newId = simctl.CreateDevice("TestDevice","iPhone 5","iOS 8.3")
            print newId
            simctl.DeleteDevice(newId)
        except Exception, e:
            print e 
        pass


if __name__ == '__main__':
    unittest.main()