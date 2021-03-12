import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class NetworkInterfaceItem(Gtk.ListBoxRow):
    def __init__(self, network_interface):
        super(Gtk.ListBoxRow, self).__init__()
        box = Gtk.Box()
        self.add(box)
        self.network_interface = network_interface
        server_image = Gtk.Image()
        server_image.set_from_icon_name(
            "network-wired",
            Gtk.IconSize.LARGE_TOOLBAR
        )
        box.pack_start(server_image, False, False, 0)
        box.pack_start(Gtk.Label.new(network_interface), True, False, 0)