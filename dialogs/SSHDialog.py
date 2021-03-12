import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

@Gtk.Template(filename="./dialogs/ssh_dialog.glade")
class SSHDialog(Gtk.Dialog):

    __gtype_name__ = 'SSHDialog'

    username_buffer = Gtk.Template.Child()
    pass_buffer = Gtk.Template.Child()
    port_buffer = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def keyPress(self, widget, event):
        if Gdk.keyval_name(event.keyval) == 'Return':
            self.emit("response", Gtk.ResponseType.OK)
            return True
        return False

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Enter credentials", parent.get_toplevel(), 0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.connect("response", self.on_response)
        self.port = "22"
    
    def on_response(self, widget, response_id):
        start_iter_user = self.username_buffer.get_start_iter()
        end_iter_user = self.username_buffer.get_end_iter()
        self.username = self.username_buffer.get_text(start_iter_user, end_iter_user, True)

        start_iter_pass = self.pass_buffer.get_start_iter()
        end_iter_pass = self.pass_buffer.get_end_iter()
        self.password = self.pass_buffer.get_text(start_iter_pass, end_iter_pass, True)

        start_iter_port = self.port_buffer.get_start_iter()
        end_iter_port = self.port_buffer.get_end_iter()
        self.port = self.port_buffer.get_text(start_iter_port, end_iter_port, True)

    def get_credentials(self):
        return [
            self.username,
            self.password,
            self.port
        ]