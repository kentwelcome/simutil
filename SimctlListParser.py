import os
import re
import sys
import unittest

class SimctlListParser(object):

    STATE_INIT          = 0
    STATE_DEVICE_TYPE   = 1
    STATE_RUNTIME       = 2
    STATE_DEVICE        = 3
    STATE_UNKNOWN       = -1

    """docstring for SimctlListParser"""
    def __init__(self, simctlOutput):
        super(SimctlListParser, self).__init__()
        self.SimctlListOutput = simctlOutput
        self.parserState = self.STATE_INIT
        self.status = {}
        self.debug = False

    def SetDebug(self, val):
        if val == True:
            self.debug = True
        else:
            self.debug = False

    def DbgPrint(self,buf):
        if self.debug == True:
            print buf

    def getStateByName(self, name):
        if name == "Device Types":
            return self.STATE_DEVICE_TYPE
        elif name == "Runtimes":
            return self.STATE_RUNTIME
        elif name == "Devices":
            return self.STATE_DEVICE
        else:
            return self.STATE_UNKNOWN

    def checkNewStatus(self,buf):
        newStatus = re.match(r'== (.+) ==',buf)
        if newStatus:
            return (self.getStateByName(newStatus.group(1)), newStatus.group(1))
        else:
            return None

    def parseDeviceTypes(self,buf):
        deviceType = re.match(r'(.+) \((.+)\)',buf)
        if deviceType:
            return {'name':deviceType.group(1),'id':deviceType.group(2)}
        else:
            return None

    def parseRuntime(self,buf):
        runtime = re.match(r'(.+) \((.+)\) \((.+)\)',buf)
        if runtime:
            return {'name':runtime.group(1), 'build':runtime.group(2), 'id':runtime.group(3)}
        else:
            return None

    def parseDeviceRunTime(self,buf):
        deviceRuntime = re.match(r'-- (.+) --',buf)
        if deviceRuntime:
            available = True
            runtime = deviceRuntime.group(1)
            if re.match(r'^Unavailable',runtime):
                available = False
            return {'runtime':runtime,'devices':[],'available':available}
        else:
            return None

    def parseAvailableDevice(self, buf):
        device = re.match(r'(.+) \((.+)\) \((.+)\)',buf)
        if device:
            return {'name':device.group(1).replace("    ",""),'id':device.group(2),'state':device.group(3)}
        else:
            return None

    def parseUnavailableDevice(self, buf):
        device = re.match(r'(.+) \((.+)\) \((.+)\) ',buf)
        if device:
            return {'name':device.group(1).replace("    ",""),'id':device.group(2),'state':device.group(3)}
        else:
            return None

    def appendDeviceByRuntime(self,runtime,device):
        for x in self.status['Devices']:
            if x['runtime'] == runtime:
                x['devices'].append(device)

    def parse(self):
        deviceState = self.STATE_INIT
        currentRuntime = ""
        for x in self.SimctlListOutput.split('\n'):
            newState = self.checkNewStatus(x)
            if newState:
                (state,name) = newState
                self.parserState = state
                deviceState = self.STATE_RUNTIME
                self.status[name.replace(" ","")] = []

            elif self.parserState == self.STATE_DEVICE_TYPE:
                newDeviceType = self.parseDeviceTypes(x)
                if newDeviceType:
                    self.status["DeviceTypes"].append(newDeviceType)

            elif self.parserState == self.STATE_RUNTIME:
                newRuntime = self.parseRuntime(x)
                if newRuntime:
                    self.status["Runtimes"].append(newRuntime)

            elif self.parserState == self.STATE_DEVICE:
                newDeviceRuntime = self.parseDeviceRunTime(x)
                if newDeviceRuntime:
                    currentRuntime = newDeviceRuntime
                    deviceState = self.STATE_DEVICE
                    self.status["Devices"].append(newDeviceRuntime)
                    pass
                elif deviceState == self.STATE_DEVICE:
                    if currentRuntime['available']:
                        newDevice = self.parseAvailableDevice(x)
                    else:
                        newDevice = self.parseUnavailableDevice(x)
                    if newDevice:
                        self.appendDeviceByRuntime(currentRuntime['runtime'],newDevice)
                        
        self.DbgPrint(self.status)
        return self.status





class TestSimctlListParser(unittest.TestCase):
    def setUp(self):
        self.realTestData = '''
== Device Types ==
iPhone 4s (com.apple.CoreSimulator.SimDeviceType.iPhone-4s)
iPhone 5 (com.apple.CoreSimulator.SimDeviceType.iPhone-5)
iPhone 5s (com.apple.CoreSimulator.SimDeviceType.iPhone-5s)
iPhone 6 Plus (com.apple.CoreSimulator.SimDeviceType.iPhone-6-Plus)
iPhone 6 (com.apple.CoreSimulator.SimDeviceType.iPhone-6)
iPad 2 (com.apple.CoreSimulator.SimDeviceType.iPad-2)
iPad Retina (com.apple.CoreSimulator.SimDeviceType.iPad-Retina)
iPad Air (com.apple.CoreSimulator.SimDeviceType.iPad-Air)
Resizable iPhone (com.apple.CoreSimulator.SimDeviceType.Resizable-iPhone)
Resizable iPad (com.apple.CoreSimulator.SimDeviceType.Resizable-iPad)
== Runtimes ==
iOS 8.3 (8.3 - 12F69) (com.apple.CoreSimulator.SimRuntime.iOS-8-3)
== Devices ==
-- iOS 8.3 --
    iPhone 4s (0640BD55-5A52-4124-B809-20EF25060200) (Shutdown)
    iPhone 5 (C86996CB-E938-4730-A454-33D9FE4A9CA0) (Shutdown)
    iPhone 5 (476DA21B-76C5-41C8-A0DE-F8D35B01F661) (Shutdown)
    iPhone 5s (FD67C89E-0593-4E98-A79D-2973F3276518) (Shutdown)
    iPhone 6 Plus (E7606153-82E3-403C-93B5-2CE066427BBB) (Shutdown)
    iPhone 6 (7EB84FF6-1698-4B23-B420-01AB5977AC5B) (Shutdown)
    iPad 2 (1E175B3A-EE4B-4A1A-906C-2371E600E0E8) (Shutdown)
    iPad Retina (9E054E5F-7F9C-4364-BD99-FD2B6D5BE915) (Shutdown)
    iPad Air (91AE1BEA-53E8-4ED4-86F1-672E5B1CBBFF) (Shutdown)
    Resizable iPhone (59B47378-AD49-4F7D-9A77-F5A3F2981BF4) (Shutdown)
    Resizable iPad (59CED3A1-1D5B-4F37-86BA-01B085851CB9) (Shutdown)
-- Unavailable: com.apple.CoreSimulator.SimRuntime.iOS-7-1 --
    iPhone 4s (239AB1E1-71C7-4836-8768-F89D878B4C76) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5 (1CB0AEE3-C12D-4EED-874D-C331F3CD33F2) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5s (BCA4A7EA-BC84-414B-BF81-6AD6EDD75A87) (Shutdown) (unavailable, runtime profile not found)
    iPad 2 (D38E75A8-0203-4DF0-ACBC-3C5E5BA6724D) (Shutdown) (unavailable, runtime profile not found)
    iPad Retina (9208A404-603F-445D-AEAD-4EB31D4751FC) (Shutdown) (unavailable, runtime profile not found)
    iPad Air (7A22BAC4-4CE1-452F-96C7-058591159673) (Shutdown) (unavailable, runtime profile not found)
-- Unavailable: com.apple.CoreSimulator.SimRuntime.iOS-8-0 --
    iPhone 4s (C740C2DC-9B51-4A6E-9B3A-706293619776) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5 (171F7927-1FF5-4141-9C2B-0CE189C154FC) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5s (25DFF684-7BB1-4831-9661-51B45AAF2680) (Shutdown) (unavailable, runtime profile not found)
    iPhone 6 Plus (F87780E5-0D42-4F0F-8EFE-BA4399B3F33B) (Shutdown) (unavailable, runtime profile not found)
    iPhone 6 (C6050CA5-AEB7-404A-90A8-0D4E42AA6CA0) (Shutdown) (unavailable, runtime profile not found)
    iPad 2 (78FCF58E-CEDD-4FC2-A56B-4297E80E8535) (Shutdown) (unavailable, runtime profile not found)
    iPad Retina (4A0C78E3-0941-4971-A37B-41BA9ECB6EF9) (Shutdown) (unavailable, runtime profile not found)
    iPad Air (A73F1A0F-EB3D-4C51-9774-F4C504FA786A) (Shutdown) (unavailable, runtime profile not found)
    Resizable iPhone (8394BE5A-6901-4778-8A0A-465A186A167A) (Shutdown) (unavailable, runtime profile not found)
    Resizable iPad (E1CB7D50-CB0B-4A28-8CE1-52CB78DD500A) (Shutdown) (unavailable, runtime profile not found)
-- Unavailable: com.apple.CoreSimulator.SimRuntime.iOS-8-1 --
    iPhone 4s (2627E0C2-9F30-409D-940F-EAA4AE76247B) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5 (13275ADE-BAA9-49B3-A9CE-B1EC9BDE9B29) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5s (F7201639-046F-4B6C-9AC1-FB3AACC557AC) (Shutdown) (unavailable, runtime profile not found)
    iPhone 6 Plus (E4FEB758-C2FD-467B-8C50-2A7FD42460A7) (Shutdown) (unavailable, runtime profile not found)
    iPhone 6 (BFB07F51-7E7A-4E02-AE07-166FEF80C840) (Shutdown) (unavailable, runtime profile not found)
    iPad 2 (CBBA40D3-644C-4D35-8352-EA56F44CF185) (Shutdown) (unavailable, runtime profile not found)
    iPad Retina (F0FEECA5-0CB2-452E-BD00-505C859DD502) (Shutdown) (unavailable, runtime profile not found)
    iPad Air (867EEE91-3D98-4646-9971-282A4C49120D) (Shutdown) (unavailable, runtime profile not found)
    Resizable iPhone (B831568D-BC09-4F4A-B1F4-0EE9EF67AA95) (Shutdown) (unavailable, runtime profile not found)
    Resizable iPad (925FAB6A-33F0-42DC-9873-02E1D415EA9D) (Shutdown) (unavailable, runtime profile not found)
-- Unavailable: com.apple.CoreSimulator.SimRuntime.iOS-8-2 --
    iPhone 4s (AF339403-2D06-4CD7-934E-94A45DA67BA2) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5 (60DB07F6-AF86-4554-B28E-C50A2A77A5DC) (Shutdown) (unavailable, runtime profile not found)
    iPhone 5s (A1853A04-D2F3-4D21-A3BB-33F9D4C9C487) (Shutdown) (unavailable, runtime profile not found)
    iPhone 6 Plus (4DB14B20-2464-4DAC-8919-633620DFA5C1) (Shutdown) (unavailable, runtime profile not found)
    iPhone 6 (8FD98430-C027-46FD-9551-17520D78F504) (Shutdown) (unavailable, runtime profile not found)
    iPad 2 (9069F212-B702-4455-9198-6DB6B9AA581A) (Shutdown) (unavailable, runtime profile not found)
    iPad Retina (D191B8DB-3845-46F6-9963-467CFE105892) (Shutdown) (unavailable, runtime profile not found)
    iPad Air (7F72A348-1572-4538-B9B1-503BA7C65937) (Shutdown) (unavailable, runtime profile not found)
    Resizable iPhone (D07F4164-C87C-44E5-B29F-68DB06B70B37) (Shutdown) (unavailable, runtime profile not found)
    Resizable iPad (E124F37D-6F05-45FE-93BC-8A54F961D948) (Shutdown) (unavailable, runtime profile not found)
'''
        self.invalidTestData = "test"
        pass

    def test_InvalidTestData(self):
        simctl = SimctlListParser(self.invalidTestData)
        status = simctl.parse()
        self.assertEquals({}, status)
        pass

    def test_ReadTestData(self):
        simctl = SimctlListParser(self.realTestData)
        status = simctl.parse()
        pass

if __name__ == '__main__':
    unittest.main()
