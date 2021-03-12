import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio
import sys
from app_window import AppWindow

class MainApp(Gtk.Application):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, application_id="com.master.diploma",
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)

    def do_activate(self) -> None:
        window = AppWindow(self)
        window.show_all()

APP = MainApp()
exit_status = APP.run(sys.argv)
sys.exit(exit_status)
