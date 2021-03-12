import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import threading
import json

from dialogs import  ManualEnteringDialog, SSHDialog
from automatic_scan import ListBoxRowWithData
from automatic_scan.AutoScanner import AutoScanner
from ssh_toolbox.SSHInit import SSHInit
from MDPClient import MDPClient
from config import default_message

@Gtk.Template(filename="./app_window.glade")
class AppWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'AppWindow'

    button_scan_auto  = Gtk.Template.Child()
    box_outer         = Gtk.Template.Child()
    button_holder_box = Gtk.Template.Child()

    obtained_credentails = False

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Server Observer", application=app)
        self.initial_methods = []
        self.mdp_client = None

        autoscanner = AutoScanner(self)
        autoscanner.connect("ipaddresses_received", self.show_servers)
        self.button_scan_auto.connect("clicked", autoscanner.scan_auto)


    def init_mdp(self, machine_key, ip_address):
        default_message["key"] = machine_key
        self.show_servers(None, [ip_address])
        self.mdp_response_received(None, (ip_address, json.dumps(default_message)))


    def prepare_ssh(self, ip_address):
        ssh_dialog = SSHDialog(self)
        response   = ssh_dialog.run()

        if response == Gtk.ResponseType.OK:
            credentials = ssh_dialog.get_credentials()
            ssh_dialog.destroy()
            self.ssh_credentials_obtained(None, (ip_address, credentials))


    @Gtk.Template.Callback()
    def add_manual(self, _):
        dialog = ManualEnteringDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            ip_address = dialog.get_selected_interface()
            dialog.hide()

            machine_key = MDPClient.check_if_known_machine(ip_address)

            if machine_key:
                self.init_mdp(machine_key, ip_address)
            else:
                self.prepare_ssh(ip_address)


    def init_ssh(self, ip_address, credentials) -> None:
        SSHInit([ip_address, *credentials])
        self.mdp_response_received(None, [ip_address])


    def ssh_credentials_obtained(self, _, credentials) -> None:
        ip_address = credentials[0]

        if hasattr(self, 'welcome_message') == False:
            self.show_servers(None, [ip_address])

        MDPClient.replace_widget(self.welcome_message, self.spinner_window)
        self.spinner_window.start()
        self.spinner_window.show_all()
        thread = threading.Thread(target=self.init_ssh, args=(ip_address, credentials[1]))
        thread.daemon = True
        thread.start()

    
    def add_list_item(self, server_item):
        listbox_row = ListBoxRowWithData(server_item)
        listbox_row.connect('mdp_machine_recognized', self.mdp_response_received)
        listbox_row.connect('ssh_credentials_obtained', self.ssh_credentials_obtained)
        listbox_row.connect('not_known_machine_display_placeholder', self.restore_message)
        return listbox_row


    def restore_message(self, *_):
        if self.scrolled_window.get_parent() != None:
            MDPClient.replace_widget(self.scrolled_window, self.welcome_message)

        self.mdp_messages_grid.hide()


    def show_servers(self, _, servers_list):
        self.box_outer.destroy()
        self.button_holder_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        builder = Gtk.Builder()
        builder.add_from_file("serverview_window.glade")
        server_window = builder.get_object("server_view_window")
        self.scrolled_window = Gtk.ScrolledWindow()
        self.welcome_message = builder.get_object("welcome_message")
        self.mdp_messages_grid = builder.get_object("mdp_messages_grid")
        self.spinner_window = Gtk.Spinner()

        listbox = builder.get_object("servers_listbox")
        for server_item in servers_list:
            listbox.add(self.add_list_item(server_item))
        
        listbox.select_row(listbox.get_row_at_index(0))

        self.button_holder_box.pack_start(server_window, True, True, 0)
        self.button_holder_box.show_all()


    def grid_update(self, _, available_methods):
        if self.initial_methods == available_methods[0]["get_available_methods"]:
            return

        self.initial_methods = available_methods[0]["get_available_methods"]
        for child in self.mdp_messages_grid.get_children():
            child.destroy()

        row = 0

        for method_name in self.initial_methods:
            method_description = self.initial_methods[method_name]

            button_mdp = Gtk.Button()
            button_mdp.set_has_tooltip(True)
            button_mdp.set_label(method_name)

            result_of_operation_text = Gtk.Label()
            result_of_operation_text.set_text("Result of " + method_name)

            def tooltip_factory(method_description):
                def show_tooltip(widget, x, y, keyboard_mode, tooltip):
                    tooltip.set_text(method_description)
                    return True
                
                return show_tooltip

            def button_click(button):
                send_message = default_message
                send_message["operations"].append(button.get_label())
                self.mdp_client.set_message(json.dumps(send_message))

            button_mdp.connect("query-tooltip", tooltip_factory(method_description))
            button_mdp.connect("clicked", button_click)
            self.mdp_messages_grid.attach(button_mdp, 0, row, 1, 1)
            self.mdp_messages_grid.attach(result_of_operation_text, 1, row, 1, 1)
            row += 1

        self.mdp_messages_grid.show_all()


    def mdp_response_received(self, _, credentials):
        if len(credentials) == 2:
            ip_address, key = credentials
            self.mdp_client = MDPClient(ip_address, key)
        elif len(credentials) == 3:
            self.mdp_client = MDPClient(credentials[2])
        elif len(credentials) == 1:
            self.mdp_client = MDPClient(credentials[0])

        if self.welcome_message.get_parent() is not None:
            MDPClient.replace_widget(self.welcome_message, self.scrolled_window)
        elif self.spinner_window.get_parent() is not None:
            MDPClient.replace_widget(self.spinner_window, self.scrolled_window)

        self.mdp_client.connect('update_grid', self.grid_update)
        self.mdp_client.run_in_window(self.scrolled_window)
        self.mdp_messages_grid.show_all()
