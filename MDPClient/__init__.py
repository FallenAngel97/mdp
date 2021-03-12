import json
import collections
import socket
import os
import select
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk

from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange, pi, random, linspace
import matplotlib.cm as cm
import numpy as np

from config import default_message
import time

class MDPClient(GObject.GObject):

    __gsignals__ = {
        'update_grid': ( GObject.SIGNAL_RUN_FIRST | GObject.SIGNAL_ACTION, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
    }

    @staticmethod
    def check_if_known_machine(ip: str):
        file_path = f'./.known_machines/{ip}.txt'

        if os.path.exists(file_path):
            with open(file_path) as machine_key:
                return machine_key.read()

        else:
            return False

    @staticmethod
    def is_json(myjson) -> bool:
        if type(myjson) is not str:
            return False
        try:
            json_object = json.loads(myjson)
        except ValueError as e:
            return False
        return True
        
    @staticmethod
    def replace_widget(old, new) -> None:
        parent = old.get_parent()

        props = {}
        for key in Gtk.ContainerClass.list_child_properties(type(parent)):
            props[key.name] = parent.child_get_property(old, key.name)

        parent.remove(old)
        parent.add(new)

        for name, value in props.items():
            parent.child_set_property(new, name, value)

    def run_in_window(self, scrolling_window) -> None:
        self.fig = Figure()
        ax = self.fig.add_subplot(111)
        self.fig.suptitle(self.ip_address, fontsize=14, fontweight='bold')
        ax.set_xlim(0, 50)
        ax.set_ylim(0, 100)

        self.ram_data = [0] * 50
        self.cpu_data = [0] * 50
        self.ram_line, = ax.plot(self.ram_data, label='RAM')
        self.cpu_line, = ax.plot(self.cpu_data, label='CPU')
        ax.legend()

        canvas = FigureCanvas(self.fig)
        if scrolling_window.get_child() != None:
            scrolling_window.remove(scrolling_window.get_child())
        scrolling_window.add_with_viewport(canvas)
        scrolling_window.show_all()

        self.sock.sendto(json.dumps(self.message).encode(), self.server_address)
        self.mdp_result()

    def __init__(self, ip: str, message=default_message) -> None:
        super(MDPClient, self).__init__()
        self.ip_address: str = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.server_address = (ip, 12345)
        self.message = message

    def update_graph(self, points_data, new_info, line) -> None:
        q = collections.deque(getattr(self, points_data))
        q.append(new_info)
        q.popleft()
        setattr(self, points_data, list(q))
        getattr(self, line).set_ydata(getattr(self, points_data))

    
    def set_message(self, message) -> None:
        self.message = message
        GLib.source_remove(self.timeout)
        self.mdp_result()

    def mdp_result(self) -> None:
        key = self.message
        try:
            if type(key) is dict:
                key = json.dumps(key)
            elif self.is_json(key) != True:
                key = f'{{"key": "{key}", "operations": ["get_cpu_percent", "get_machine_memory", "get_available_methods"] }}'

            # 0.2 ms - 0.06 ms
            self.sock.sendto(key.encode(), self.server_address)
            data = self.sock.recvfrom(1024)
            machine_info = json.loads(data[0].decode("utf-8"))
            if machine_info["status"] == False:
                key = machine_info["machine_key"]
                self.message = key
                with open(f"./.known_machines/{self.ip_address}.txt", 'w') as key_file:
                    key_file.write(key)
                GLib.timeout_add(1000, self.mdp_result)
                return
            
            self.update_graph("ram_data", machine_info["get_machine_memory"][2], "ram_line")
            self.update_graph("cpu_data", machine_info["get_cpu_percent"], "cpu_line")
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.emit('update_grid', (machine_info, ))
        except socket.error:
            pass

        self.timeout = GLib.timeout_add(1000, self.mdp_result)

GObject.type_register(MDPClient)