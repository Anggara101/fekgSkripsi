from threading import Thread
import socket
import csv
import numpy as np

from kivy.properties import NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy_garden.graph import MeshLinePlot, PointPlot
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineListItem

# import preprocesing
# import Clustering

Builder.load_file('main.kv')


class Backdrop(MDScreen):
    state_connection = NumericProperty(1)
    zoom = NumericProperty(1)
    n = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize state
        self.state_connection = 0
        # Declare instance variable for socket
        self.host = 'B8:27:EB:6D:DB:12'
        self.port = 9
        self.s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        # Declare instance variable for procesing signal
        self.window_size = 2000
        self.state_show = 1
        # Declare instance variable for graph
        self.zoom = 1
        self.n = 1
        self.xmin = 0
        self.xmax = 5000
        self.scroll = self.ids.view
        self.graph = self.ids.graph
        self.plot = MeshLinePlot(color=[0, 0, 1, 1])
        self.plot_den = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot_peak1 = PointPlot(point_size=4, color=[0, 1, 0, 1])
        self.graph.add_plot(self.plot)
        self.graph.add_plot(self.plot_den)
        self.graph.add_plot(self.plot_peak1)

    def connect(self):
        # State 0 = socket is disconnected
        if self.state_connection == 0:
            # Connect to server
            try:
                self.s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                self.s.connect((self.host, self.port))
                toast('Connected to server with MAC address: ' + self.host)
                # Update State
                self.s.sendall('1'.encode())
                self.state_connection = 1
                print(self.state_connection)
                self.ids.backdrop.open()
            except TimeoutError:
                toast('Server is taking too long to respon')
            except OSError:
                toast('Server is down!')

        # State 1 = socket is connected
        elif self.state_connection == 1:
            # Close connection
            self.s.sendall('0'.encode())
            self.s.close()
            # Update State
            self.state_connection = 0
            toast('Disconnected')
            print(self.state_connection)
        # State 2 = Client want server to send data
        # State 3 = Offline mode
        else:
            pass

    def start_reading(self):
        # State 2: start new thread for reading from socket
        if self.state_connection == 1:
            self.state_connection = 2
            self.s.sendall('2'.encode())
            print(self.state_connection)
            t = Thread(target=self.read_data)
            t.start()
        # State 3: start new thread for reading from COM port
        if self.state_connection == 3:
            self.state_connection = 4
            self.update_connect()
            t = Thread(target=self.offline_sensor)
            t.start()

        global x_raw, ekg_raw, x, ekg, ekg_peak1
        x_raw, ekg_raw, x, ekg, ekg_peak1 = [], [], [], [], []
        Clock.schedule_interval(self.get_value, 0.001)
        # Reset Graph
        self.n = 1
        self.zoom = 1
        self.xmin = 0
        self.xmax = 5000
        self.graph.xmin = self.xmin
        self.graph.xmax = self.xmax
        self.scroll.scroll_x = 0
        self.ids.view2.width = self.scroll.width * self.zoom * self.n
        self.window_size = 2000

    def read_data(self):
        global x_raw, ekg_raw
        t = 0
        toast('Process Started')
        while True:
            data_sensor = self.s.recv(1024)
            if data_sensor is not None:
                if self.state_connection != 2:
                    break
                data_sensor = data_sensor.decode().rstrip()
                line = list(data_sensor.split(","))
                try:
                    t = float(line[0])
                    value = float(line[1])
                    print(t, value)
                    x_raw.append(t)
                    ekg_raw.append(value)
                except ValueError:
                    pass
                # if t >= self.window_size:
                #     self.window_size += 2000
                #     if self.state_show != 1:
                #         t2 = Thread(target=self.akuisisi)
                #         t2.start()
                #         print('processing')
                if t >= self.xmax:
                    self.n += 1
                    self.xmax = self.xmax + 5000
                    self.scroll.scroll_x = 1
                    self.ids.view2.width = self.scroll.width * self.zoom * self.n
                    self.graph.xmin = self.xmin
                    self.graph.xmax = self.xmax

    def stop_reading(self):
        # Clock.unschedule(self.read_data)
        Clock.unschedule(self.get_value)
        if self.state_connection == 2:
            self.s.sendall('1'.encode())
            self.state_connection = 1
        else:
            self.state_connection = 3
        self.update_connect()

    def get_value(self, _):
        self.plot.points = [(x_raw[i], j) for i, j in enumerate(ekg_raw)]

    def update_zoom(self, value):
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            # self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            # self.graph.x_ticks_major *= 2

    def load(self):
        global x_raw, ekg_raw
        x_raw = []
        ekg_raw = []
        f = open('data4.csv', 'r')
        plots = csv.reader(f)
        for row in plots:
            x_raw.append(float(row[0]))
            ekg_raw.append(float(row[1]))
        f.close()
        self.ids.backdrop.open()
        x_raw = np.array(x_raw) * 1000
        # x = x_raw
        # ekg = preprocesing.pp(x, np.array(ekg_raw), show=False)
        self.plot.points = [(x_raw[i], j) for i, j in enumerate(ekg_raw)]
        # self.plot_den.points = [(x[i], j) for i, j in enumerate(ekg)]
        # ekg_amp, ekg_peak, ns = preprocesing.peakvalley(ekg, show=False)
        # ekg_peak1, ekg_peak2 = Clustering.case1(ekg_amp, ekg_peak, ekg, ns, show=False)
        # self.plot_peak1.points = [(x[j], ekg[j]) for i, j in enumerate(ekg_peak1)]

        self.xmax = len(x_raw)
        self.scroll.scroll_x = 1
        self.ids.view2.width = self.scroll.width * self.zoom
        self.graph.xmin = self.xmin
        self.graph.xmax = self.xmax

    def checkbox_show(self):
        if self.ids.denoise.active is True and self.ids.cluster.active is False:
            self.state_show = 2
        elif self.ids.denoise.active is False and self.ids.cluster.active is True:
            self.state_show = 3
        elif self.ids.denoise.active is True and self.ids.cluster.active is True:
            self.state_show = 4
        elif self.ids.denoise.active is False and self.ids.cluster.active is False:
            self.state_show = 1
        print(self.state_show)

    # def akuisisi(self):
    #     global x_raw, ekg_raw, x, ekg, ekg_peak1
    #     x = np.array(x_raw)
    #     ekg = preprocesing.pp(x, np.array(ekg_raw), show=False)
    #     if self.state_show == 2:
    #         self.plot_den.points = [(x[i], j) for i, j in enumerate(ekg)]
    #
    #     if self.state_show == 3 or self.state_show == 4:
    #         ekg_amp, ekg_peak, ns = preprocesing.peakvalley(ekg, show=False)
    #         ekg_peak1, ekg_peak2 = Clustering.case1(ekg_amp, ekg_peak, ekg, ns, show=False)
    #         if self.state_show == 3:
    #             self.plot_peak1.points = [(x_raw[j], ekg_raw[j]) for i, j in enumerate(ekg_peak1)]
    #         if self.state_show == 4:
    #             self.plot_den.points = [(x[i], j) for i, j in enumerate(ekg)]
    #             self.plot_peak1.points = [(x[j], ekg[j]) for i, j in enumerate(ekg_peak1)]
    #     print('pre processing complete!')

    def generate(self):
        for i in range(3):
            self.ids.container.add_widget(TwoLineListItem(text=f"Single-line item {i}",
                                                          secondary_text="subtitle",
                                                          on_release=lambda y: toast(y.text)))
        print("loop ended")

    def turn_off(self):
        self.s.sendall('10'.encode())

    def on_leave(self, *args):
        self.s.close()


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

    def build(self):
        return Backdrop()


if __name__ == '__main__':
    x_raw, ekg_raw = [], []
    MainApp().run()
