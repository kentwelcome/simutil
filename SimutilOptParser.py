import os
import sys
import argparse
import unittest


class SimutilOptParser(object):
    
    def __init__(self, args):
        super(SimutilOptParser, self).__init__()
        self.args = args
        #self.supportCmds = self.initCmds()
        pass

    # TODO: replace hard code command by supportCmds
    def initCmds(self):
        cmds = []
        cmds.append({'cmd':'list', 
                    'help':'Show the status of iOS Simulator.'})
        cmds.append({'cmd':'create', 
                    'help':'Create new device of iOS Simulator.'})
        cmds.append({'cmd':'delete', 
                    'help':'Delete new device of iOS Simulator.'})
        cmds.append({'cmd':'launch', 
                    'help':'Launch iOS Simulator with selected device.'})
        cmds.append({'cmd':'install', 
                    'help':'Install iOS application into selected device.'})
        cmds.append({'cmd':'uninstall',
                    'help':'Uninstall iOS application from selected device.'})
        return cmds

    def add_list_commands(sell, cmd):
        cmd.add_argument('-d', '--device', dest='deviceName', action='store', 
                         type=str, default=None, metavar='DeviceName', 
                         required=False, help='Select device name')

    def add_create_commands(self, cmd):
        cmd.add_argument(dest='deviceName', action='store', 
                         type=str, default=None, metavar='name', 
                         help='Create device name.')
        cmd.add_argument(dest='runtimeName', action='store', 
                         type=str, default=None, metavar='runtime', 
                         help='Create device with runtime. (ex. iOS 8.3)')
        cmd.add_argument(dest='deviceType', action='store', 
                         type=str, default=None, metavar='type', 
                         help='Create device with device type. (ex. iPhone 6, iPhone 5s, etc...)')
        pass

    def add_delete_commands(self, cmd):
        cmd.add_argument(dest='deviceName', action='store', 
                         type=str, default=None, metavar='name', 
                         help='Delete device name.')
        cmd.add_argument(dest='runtimeName', action='store', 
                         type=str, default=None, metavar='runtime', 
                         help='Delete device with runtime. (ex. iOS 8.3)')
        pass

    def add_launch_commands(self, cmd):
        cmd.add_argument(dest='deviceName', action='store', 
                         type=str, default=None, metavar='name', 
                         help='Launch iOS Simulator with device name.')
        cmd.add_argument(dest='runtimeName', action='store', 
                         type=str, default=None, metavar='runtime', 
                         help='Launch device with runtime. (ex. iOS 8.3)')
        cmd.add_argument('--record', dest='record', action='store_true', default=False,
                         help='Record iOS Simulator screen into movie file.')

    def add_install_commands(self, cmd):
        cmd.add_argument(dest='appPath', action='store', 
                         type=str, default=None, metavar='app_path', 
                         help='Install iOS Appliction with path')
        cmd.add_argument(dest='deviceName', action='store', 
                         type=str, default=None, metavar='device_name', 
                         help='Install iOS Appliction into device')
        cmd.add_argument(dest='runtimeName', action='store', 
                         type=str, default=None, metavar='runtime', 
                         help='Install iOS Appliction into device with runtime. (ex. iOS 8.3)')
        pass

    def add_uninstall_commands(self, cmd):
        cmd.add_argument(dest='appPath', action='store', 
                         type=str, default=None, metavar='app_path', 
                         help='Uninstall iOS Appliction with path')
        cmd.add_argument(dest='deviceName', action='store', 
                         type=str, default=None, metavar='device_name', 
                         help='Uninstall iOS Appliction from device')
        cmd.add_argument(dest='runtimeName', action='store', 
                         type=str, default=None, metavar='runtime', 
                         help='Uninstall iOS Appliction from device with runtime. (ex. iOS 8.3)')
        pass

    def parse(self):
        optParser = argparse.ArgumentParser(description='Utility to cotrol iOS Simulator.')

        cmdParsers  = optParser.add_subparsers(dest='cmd', help='Support subcommands')
        listCmd     = cmdParsers.add_parser('list', description='Show the status of iOS Simulator.', 
                                            help='Show the status of iOS Simulator.')
        self.add_list_commands(listCmd)

        createCmd   = cmdParsers.add_parser('create', description='Create new device of iOS Simulator.',
                                            help='Create new device of iOS Simulator.')
        self.add_create_commands(createCmd)

        deleteCmd   = cmdParsers.add_parser('delete', help='Delete new device of iOS Simulator.')
        self.add_delete_commands(deleteCmd)

        launchCmd   = cmdParsers.add_parser('launch', help='Launch iOS Simulator with selected device.')
        self.add_launch_commands(launchCmd)

        installCmd  = cmdParsers.add_parser('install', help='Install iOS application into selected device.')
        self.add_install_commands(installCmd)

        uninstallCmd= cmdParsers.add_parser('uninstall', help='Uninstall iOS application from selected device.')
        self.add_uninstall_commands(uninstallCmd)

        return optParser.parse_args(self.args[1:])
    
class TestSimutilOptParser(unittest.TestCase):
    def setUp(self):
        print "Running:", self._testMethodName

    def runOptParser(self, optStr):
        try:
            opts = optStr.split()
            opts.insert(0,'simutil')
            optParser = SimutilOptParser(opts).parse()
        except SystemExit:
            pass

    def test_no_args(self):
        self.runOptParser('')
    
    def test_args_h(self):
        self.runOptParser('-h')
        pass

    def test_args_list(self):
        self.runOptParser('list -h')
        pass

    def test_args_create(self):
        self.runOptParser('create -h')
        pass

    def test_args_delete(self):
        self.runOptParser('delete -h')
        pass

    def test_args_launch(self):
        self.runOptParser('launch -h')
        pass

    def test_args_install(self):
        self.runOptParser('install -h')
        pass

    def test_args_uninstall(self):
        self.runOptParser('uninstall -h')
        pass

if __name__ == '__main__':
    unittest.main(exit=False)
