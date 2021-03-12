import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os

class ManualEnteringDialog(Gtk.Dialog):

    def keyPress(self, widget, event):
        if Gdk.keyval_name(event.keyval) == 'Return':
            self.emit("response", Gtk.ResponseType.OK)
            return True
        return False

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Enter ip address", parent, 0)

        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.connect("response", self.on_response)

        wrapper_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        description_label = Gtk.Label("Enter ip address")
        wrapper_box.pack_start(description_label, False, False, 0)
        self.ip_buffer = Gtk.TextBuffer()
        self.ip_textbox = Gtk.TextView(buffer=self.ip_buffer)
        self.ip_textbox.connect('key-press-event', self.keyPress)
        wrapper_box.pack_start(self.ip_textbox, False, False, 0) 
        box = self.get_content_area()
        box.add(wrapper_box)
        self.show_all()

    def on_response(self, widget, response_id):
        start_iter_user = self.ip_buffer.get_start_iter()
        end_iter_user = self.ip_buffer.get_end_iter()
        self.ip_address = self.ip_buffer.get_text(start_iter_user, end_iter_user, True)

    def get_selected_interface(self):
        return self.ip_address

