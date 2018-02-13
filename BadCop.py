#!/usr/bin/env python3
from os import remove
from pickle import dump, load
from sys import exit
from wx import Dialog, StaticText, Button, EVT_CLOSE, EVT_BUTTON, BoxSizer, VERTICAL, App, Icon
from wx import HORIZONTAL, ALL, CENTER, EXPAND, Size, BITMAP_TYPE_ICO
from usb.core import Configuration, find


class MainDialog(Dialog):
    """
    Main window. Hit a button to profile the system, then another to scan what was plugged in
    """

    def __init__(self):
        """Constructor"""
        Dialog.__init__(self, None, title="Bad Cop", size=Size(500, 100))
        ico = Icon('logo.ico', BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.message = StaticText(self, label="Click Profile, then insert device and click Test")
        self.profile = Button(self, label="Profile")
        self.test = Button(self, label="Test")
        self.test.Disable()
        self.profile.Bind(EVT_BUTTON, self.profileusb)
        self.test.Bind(EVT_BUTTON, self.testusb)
        self.Bind(EVT_CLOSE, self.onclose)
        main_sizer = BoxSizer(VERTICAL)
        t_sizer = BoxSizer(HORIZONTAL)
        p_sizer = BoxSizer(HORIZONTAL)
        t_sizer.Add(self.message, 0, ALL | CENTER, 5)
        p_sizer.Add(self.profile, 0, ALL | CENTER, 5)
        p_sizer.Add(self.test, 0, ALL | CENTER, 5)
        main_sizer.Add(p_sizer, 0, ALL | CENTER, 5)
        main_sizer.Add(t_sizer, 0, ALL | EXPAND | CENTER, 5)
        self.SetSizer(main_sizer)

    def profileusb(self, other):
        del other
        dev = find(find_all=True)
        devices = []
        for cfg in dev:
            devclass = str(cfg.bDeviceClass)
            product = str(cfg.iProduct)
            vid = hex(cfg.idVendor)
            pid = hex(cfg.idProduct)
            for line in Configuration(find(idVendor=cfg.idVendor)):
                line = str(line)
                linestrip = line.strip()
                linesplit = linestrip.split('\n')
                linesplit = [x.split(':') for x in linesplit]
                lines = []
                for w in linesplit:
                    lines.append([y.strip(' ') for y in w])
                for e in lines:
                    if 'bInterfaceClass' in e[0]:
                        intclass = e[1]
                        devices.append([devclass, product, vid, pid, intclass])
        with open('devices.pkl', 'wb') as f:
            dump(devices, f)
        self.profile.SetLabel("Done!")
        self.profile.Disable()
        self.test.Enable()

    def testusb(self, other):
        del other
        with open('devices.pkl', 'rb') as f:
            benchmark = load(f)
        dev = find(find_all=True)
        devices = []
        for cfg in dev:
            devclass = str(cfg.bDeviceClass)
            product = str(cfg.iProduct)
            vid = hex(cfg.idVendor)
            pid = hex(cfg.idProduct)
            for line in Configuration(find(idVendor=cfg.idVendor)):
                line = str(line)
                linestrip = line.strip()
                linesplit = linestrip.split('\n')
                linesplit = [x.split(':') for x in linesplit]
                lines = []
                for w in linesplit:
                    lines.append([y.strip(' ') for y in w])
                for e in lines:
                    if 'bInterfaceClass' in e[0]:
                        intclass = e[1]
                        devices.append([devclass, product, vid, pid, intclass])
        first_tuple_list = [tuple(lst) for lst in benchmark]
        secnd_tuple_list = [tuple(lst) for lst in devices]
        first_set = set(first_tuple_list)
        secnd_set = set(secnd_tuple_list)
        output = ""
        height = 100
        first = 0
        for devclass, product, vid, pid, usbtype in first_set.symmetric_difference(secnd_set):
            if usbtype == "0xa CDC Data":
                devicedesc = "Virtual Data Port (Network)"
            elif usbtype == "0xe0 Wireless Controller":
                devicedesc = "Wireless Internet Or Bluetooth"
            elif usbtype == "0x8 Mass Storage":
                devicedesc = "Data Storage Device"
            elif usbtype == "0x9 Hub":
                devicedesc = "USB Hub"
            elif usbtype == "0x3 Human Interface Device":
                devicedesc = "Keyboard, Mouse, or Other Input Device"
            elif usbtype == "0x2 CDC Communication":
                devicedesc = "Vitual Communications Port (Network)"
            else:
                devicedesc = usbtype + " device "
            if first == 0:
                output += "This appears to be a: \n                     " + devicedesc + " \n"
            else:
                output += "                     " + devicedesc + " \n"
            height = height + 30
            first = 1
        self.SetSize((500, height))
        self.message.SetLabel(output)

    def onclose(self, event):
        del event
        try:
            remove('devices.pkl')
        except:
            print('file missing')
        self.Destroy()
        exit("Application Exited")


app = App()
frame = MainDialog()
app.SetTopWindow(frame)
frame.Show()
app.MainLoop()
