import nmap
import ipaddress
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import shutil
from dialogs import InterfaceChooserDialog
import netifaces as ni

class AutoScanner(GObject.GObject):

    __gsignals__ = {
        'ipaddresses_received': ( GObject.SIGNAL_RUN_FIRST | GObject.SIGNAL_ACTION, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, parent):
        self.parent = parent
        GObject.GObject.__init__(self)

    def organize_hosts(self, ip_with_mask):
        nm = nmap.PortScanner()
        network_interface = ipaddress.IPv4Interface(ip_with_mask['addr']+'/'+ip_with_mask['netmask'])
        nm.scan(hosts=str(network_interface.network), arguments="-sn")
        return nm.all_hosts()

    def scan_auto(self, button):
        if shutil.which("nmap") == None:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Seems, nmap is not installed.\nPlease, make sure that it is in OS PATH variable")
            dialog.run()
            dialog.destroy()
        else:
            dialog = InterfaceChooserDialog(self.parent)
            response = dialog.run()
            while True:
                if response == Gtk.ResponseType.OK:
                    selected_interface = dialog.get_selected_interface()
                    ni.ifaddresses(selected_interface)
                    if ni.AF_INET in ni.ifaddresses(selected_interface):
                        ip = ni.ifaddresses(selected_interface)[ni.AF_INET][0]
                        dialog.hide()
                        self.servers_list = self.organize_hosts(ip)  
                        self.emit("ipaddresses_received", self.servers_list)
                        break
                    else:
                        print("This interface has no ip address!")
                        dialog_no_ip = Gtk.MessageDialog(parent=None, flags=0, message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK, text="This interface has no ip address.\nPlease, select another one")
                        dialog_no_ip.run()
                        dialog_no_ip.hide()
                        dialog.hide()
                        response = dialog.run()

                else:
                    dialog.hide()
                    break