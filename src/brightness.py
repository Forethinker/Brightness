# -*- coding:utf-8 -*-

import sys
import wx
import argparse
import subprocess
from os import system
from os import path
from time import sleep

class BrightnessController(wx.Frame):

    def debug_true(self):
        return False

    def detect_display_devices(self):
        """Detects available displays"""
        connected_devs = []

        xrandr_output = subprocess.check_output('xrandr -q', shell=True)

        lines = xrandr_output.split('\n')
        for line in lines:
            words = line.split(' ')
            for word in words:
                if word == 'connected':
                    connected_devs.append(words[0])
        return connected_devs

    def detect_calise_file(self):
        calise = {}
        with open(path.expanduser("~/.config/calise/default.conf")) as f:
            for line in f:
                if line[0] != '[' and not line[0].isspace():
                    opt_parsed = line.split('=') 
                    if len(opt_parsed) == 2:
                        key, val = opt_parsed
                        calise[key.strip()] = val.strip()
        f.close()
        return calise

    def calise_loop(self, time_sec):
        self.calise_opt = self.detect_calise_file()
        while 1:
            with open(self.calise_opt["path"]) as sys_brightness:
                numer = (int(sys_brightness.readline())+self.offset)*100
                denom = int(self.calise_opt["steps"])+self.offset
                val = int(numer/denom)
                if self.verbose:
                    print numer, '/', denom, '=', val
                system(self.cmds_secondary_display[val])
            sys_brightness.close()
            sleep(time_sec)


    def __init__(self, parent, title, args=None):
        if not args:
            super(BrightnessController, self).__init__(parent, title=title,
                                                   size=(325, 100))
        else:
            self.interval = args.interval
            self.offset = args.offset
            self.verbose = args.verbose
        self.detected_devices = self.detect_display_devices()
        self.no_of_detected_device = len(self.detected_devices)

        if self.no_of_detected_device == 1 or self.no_of_detected_device == 2:
            if self.debug_true():
                print 'Found one'
            self.primary_name = self.detected_devices[0]
        else:
            self.primary_name = 'Not Found!'
        if self.no_of_detected_device == 2:
            if self.debug_true():
                print 'Found two'
            self.secondary_name = self.detected_devices[1]
        else:
            self.secondary_name = 'Not Found'

        self.array_value = 0.00
        self.cmds_primary_display = []
        self.cmds_secondary_display = []

        for i in xrange(0, 101):
            cmd_primary_display = "xrandr --output \
                %s --brightness %s" % (self.primary_name, self.array_value)
            cmd_secondary_display="xrandr --output \
                %s --brightness %s" % (self.secondary_name, self.array_value)
            self.cmds_primary_display.append(cmd_primary_display)
            self.cmds_secondary_display.append(cmd_secondary_display)
            self.array_value += 0.01

        self.about_me_message = '''
        # Brightness Controller v1.0.1

        This application provides a GUI to
        change brightness of Primary and Secondary
        Display.
        Source available at
        https://github.com/lordamit/Brightness.
        '''

        if not args:
            self.InitUI()
            self.Center()
            self.Show()
        else:
            self.calise_loop(self.interval)


    def InitUI(self):

        panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        button_about = wx.Button(panel, label='?', size=(25, 25))
        button_about.Bind(wx.EVT_BUTTON, self.about_dialog)
        self.vbox.Add(button_about, flag=wx.ALIGN_RIGHT)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        if self.no_of_detected_device == 1 or self.no_of_detected_device == 2:
            st1 = wx.StaticText(panel, label='   Primary')
            hbox1.Add(st1, flag=wx.RIGHT | wx.TOP, border=3)
            slider1 = wx.Slider(panel,
                            value=100,
                            minValue=1,
                            maxValue=100,
                            size=(200, -1),
                            style=wx.SL_HORIZONTAL)

            hbox1.Add(slider1, flag=wx.LEFT | wx.RIGHT,
                  border=25)
            slider1.Bind(wx.EVT_SCROLL, self.primary_scroll)
        else:
            st1 = wx.StaticText(panel, label='   Primary Not Found')
            hbox1.Add(st1, flag=wx.RIGHT | wx.TOP, border=3)

        self.vbox.Add(hbox1)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        if self.no_of_detected_device == 2:
            st2 = wx.StaticText(panel, label='   Secondary')
            self.hbox2.Add(st2, flag=wx.RIGHT | wx.TOP, border=3)
            slider2 = wx.Slider(panel,
                            value=100,
                            minValue=1,
                            maxValue=100,
                            size=(200, -1),
                            style=wx.SL_HORIZONTAL)
            self.hbox2.Add(slider2, flag=wx.LEFT,
                  border=7)

            slider2.Bind(wx.EVT_SCROLL, self.secondary_scroll)
        else:
            st2 = wx.StaticText(panel, label='   Secondary Not found')
            self.hbox2.Add(st2, flag=wx.RIGHT | wx.TOP, border=3)
        self.vbox.Add(self.hbox2)

        panel.SetSizer(self.vbox)

    def primary_scroll(self, event):
        """Controls the brightness of primary monitor"""
        obj = event.GetEventObject()
        val = obj.GetValue()

        system(self.cmds_primary_display[val])

    def secondary_scroll(self, event):
        """Controls the brightness of secondary monitor"""
        obj = event.GetEventObject()
        #val = obj.GetValue()
        system(self.cmds_secondary_display[val])

    def about_dialog(self, event):
        """Shows the about message of Brightness Controller"""
        wx.MessageBox(self.about_me_message, 'About',
            wx.OK | wx.ICON_INFORMATION)

def argsparser(arglist=None, version=None):
    parser = argparse.ArgumentParser(
            description=("Change either primary or secondary monitor's brightness.\n"
            "Compatible with Calise (http://calise.sourceforge.net/wordpress/)\n"
            "For usage instruction type \"%(prog)s --help\".")
        )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%s %s' % (parser.prog, version),
        help=("display current version and exits")
        )
    parser.add_argument(
        '-i', 
        '--interval',
        metavar='N',
        dest='interval',
        type=int,
        default=120,
        help=("time interval to check up on the ambient brigthness")
        )
    parser.add_argument(
        '-o',
        '--offset',
        metavar='N',
        dest='offset',
        type=int,
        default=20,
        help=("monitor specific offset")
        )
    parser.add_argument(
        '-vv',
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help=("suppress the output")
        )
    parser.add_argument(
        '-c',
        '--command_line',
        dest='commnad_line',
        action='store_true',
        default=False,
        help=("no GUI")
        )
    return parser.parse_args()



if __name__ == '__main__':
    args = argsparser()
    if args.verbose:
        print "ARGS: ", args
    if len(sys.argv) > 1:
        BrightnessController(None, title='Brightness Controller', args=args)
    else:
        app = wx.App()
        BrightnessController(None, title='Brightness Controller')
        app.MainLoop()
