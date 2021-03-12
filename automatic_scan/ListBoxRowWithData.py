import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
import re
import locale # https://github.com/pyinvoke/invoke/issues/384

from dialogs.SSHDialog import SSHDialog
from ssh_toolbox.SSHInit import SSHInit
from MDPClient import MDPClient

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

signal_general = ( GObject.SIGNAL_RUN_FIRST | GObject.SIGNAL_ACTION, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))

class ListBoxRowWithData(Gtk.ListBoxRow):

    __gsignals__ = {
        k: signal_general for k in [
            'not_known_machine_display_placeholder',
            'mdp_machine_recognized', 
            'ssh_credentials_obtained'
        ]
    }

    def __init__(self, ip_address: str):
        super(Gtk.ListBoxRow, self).__init__()

        event_box = Gtk.EventBox()
        box = Gtk.Box()
        event_box.add(box)
        self.add(event_box)
        self.ip_address = ip_address
        server_image = Gtk.Image()
        server_image.set_from_icon_name(
            "network-server",
            Gtk.IconSize.LARGE_TOOLBAR
        )
        box.pack_start(server_image, False, False, 0)
        box.pack_start(Gtk.Label.new(ip_address), True, False, 0)
        
        menu = Gtk.Menu()
        self.machine_key = MDPClient.check_if_known_machine(self.ip_address)
        self.known_machine = (self.machine_key != False)
        
        if not self.known_machine:
            menu_item = Gtk.MenuItem("SSH into machine")
            menu_item.connect('activate', self.input_credentials_ssh)
            menu.append(menu_item)
        else:
            menu_item = Gtk.MenuItem('Connect to backup cluster')
            menu_item.connect('activate', self.connect_to_cluster)
            menu.append(menu_item)
        menu_item.show()

        event_box.connect_object("button-press-event", self._on_button_press_event, menu)

    def _on_button_press_event(self, widget, event):
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return

        if event.button == 3:
            widget.popup(None, None, None, button=event.button, activate_time=event.time, data=None)
        elif event.button == 1:
            if self.known_machine:
                self.emit("mdp_machine_recognized", (self.ip_address, self.machine_key))
            else:
                self.emit("not_known_machine_display_placeholder", {})

    def input_credentials_ssh(self, widget):
        dialog = SSHDialog(self)
        response_dialog = dialog.run()
        if response_dialog == Gtk.ResponseType.OK:
            self.emit('ssh_credentials_obtained', (self.ip_address, dialog.get_credentials()))
        dialog.hide()

    def connect_to_cluster(self):
        pass

GObject.type_register(ListBoxRowWithData)
