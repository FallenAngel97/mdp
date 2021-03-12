import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from automatic_scan import NetworkInterfaceItem
import netifaces

class InterfaceChooserDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Choose interface", parent=parent, flags=0)

        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        self.connect("response", self.on_response)

        wrapper_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        description_label = Gtk.Label("Select interface to scan")
        wrapper_box.pack_start(description_label, False, False, 0)
        self.listbox = Gtk.ListBox()
        networkcard_names = netifaces.interfaces()
        
        for networkcard in networkcard_names:
            self.listbox.add(NetworkInterfaceItem(networkcard))

        self.selected_interface = self.listbox.get_row_at_index(0)
        self.listbox.select_row(self.selected_interface)
        wrapper_box.pack_start(self.listbox, False, False, 0)
        box = self.get_content_area()
        box.add(wrapper_box)
        self.show_all()

    def on_response(self, widget, response_id):
        self.selected_interface = self.listbox.get_selected_row()

    def get_selected_interface(self):
        return self.selected_interface.network_interface
