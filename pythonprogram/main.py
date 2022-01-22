# Same as before, with a kivy-based UI

"""
Bluetooth/Pyjnius example
=========================

This was used to send some bytes to an arduino via bluetooth.
The app must have BLUETOOTH and BLUETOOTH_ADMIN permissions (well, i didn't
tested without BLUETOOTH_ADMIN, maybe it works.)

Connect your device to your phone, via the bluetooth menu. After the
pairing is done, you'll be able to use it in the app.
"""

from threading import Thread
from jnius import autoclass
from jnius import cast
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.screen import MDScreen
from kivy_garden.graph import MeshLinePlot, PointPlot

from android.broadcast import BroadcastReceiver

Builder.load_file('fekg.kv')
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
Intent = autoclass('android.content.Intent')
IntentFilter = autoclass('android.content.IntentFilter')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
UUID = autoclass('java.util.UUID')
InputStreamReader = autoclass('java.io.InputStreamReader')
BufferedReader = autoclass('java.io.BufferedReader')

# IntentFilter = autoclass('android.content.IntentFilter')

class Backdrop(MDScreen):
    state_connection = NumericProperty(1)
    zoom = NumericProperty(1)
    n = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_connection = 0
        # initiate bluetooth
        self.BtAdapter = BluetoothAdapter.getDefaultAdapter()
        if not self.BtAdapter.isEnabled():
            self.ids.btn_on_off.text = 'Disable'
        action = BluetoothAdapter.ACTION_STATE_CHANGED
        self.br = BroadcastReceiver(self.on_broadcast, actions=[action])
        self.br.start()

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
        self.graph.add_plot(self.plot)
        # self.plot_den = MeshLinePlot(color=[1, 0, 0, 1])
        # self.plot_peak1 = PointPlot(point_size=4, color=[0, 1, 0, 1])
        # self.graph.add_plot(self.plot_den)
        # self.graph.add_plot(self.plot_peak1)

    def on_off(self):
        if self.BtAdapter is None:
            toast('Device does not have Bluetooth')
            return
        else:
            # State 0 = socket is disconnected
            if self.state_connection == 0:
                # Bluetooth disabled, enabling bluetooth
                if not self.BtAdapter.isEnabled():
                    enableBTIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
                    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                    currentActivity.startActivityForResult(enableBTIntent, 0)
                else:
                    # Bluetooth enabled, disabling bluetooth
                    self.BtAdapter.disable()
            # State 1 = socket is connected
            elif self.state_connection == 1:
                # Close connection
                self.send_stream.write('0'.encode())
                self.socket.close()
                self.state_connection = 0
                self.ids.btn_on_off.text = 'Disable'
                toast('Disconnected')

    def on_broadcast(self, context, intent):
        state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR)
        if state == BluetoothAdapter.STATE_ON:
            toast("Bluetooth on")
            self.ids.btn_on_off.text = 'Disable'
            # toast('Bluetooth enabled')
            BondedDevices = BluetoothAdapter.getBondedDevices().toArray()
            for device in BondedDevices:
                # Logger.info('Im in the loop!!' + str(device))
                self.name = device.getName()
                if self.name == "raspberrypi":
                    address = device.getAddress()
                    self.ids.list_devices.add_widget(TwoLineListItem(text=str(self.name),
                                                                     secondary_text=str(address),
                                                                     on_release=lambda x: self.connect(device)))
        if state == BluetoothAdapter.STATE_TURNING_ON:
            toast("Turning on Bluetooth")
        if state == BluetoothAdapter.STATE_OFF:
            toast("Bluetooth off")
            self.ids.btn_on_off.text = 'Enable'
            self.ids.list_devices.clear_widgets()
        if state == BluetoothAdapter.STATE_TURNING_OFF:
            toast("Turning off Bluetooth")

    def on_leave(self, *args):
        self.br.stop()

    def connect(self, device):
        # State 0 = socket is disconnected
        if self.state_connection == 0:
            self.socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee"))
            input_stream = self.socket.getInputStream()
            self.recv_stream = BufferedReader(InputStreamReader(input_stream))
            self.send_stream = self.socket.getOutputStream()
            # Connect to server
            try:
                self.socket.connect()
                toast('Connected to server : ' + device.getName())
                self.send_stream.write('1'.encode())
                # send_stream.flush()
                self.state_connection = 1
                self.ids.btn_on_off.text = 'Disconnect'
                self.ids.backdrop.open()
            except OSError:
                toast("Server is down!")

    def update_zoom(self, value):
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            self.graph.x_ticks_major *= 2

    def start_reading(self):
        # State 2: start new thread for reading from socket
        if self.state_connection == 1:
            self.state_connection = 2
            self.send_stream.write('2'.encode())
            t = Thread(target=self.read_data)
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
            if self.recv_stream.ready():
                try:
                    data_sensor = self.recv_stream.readLine()
                    line = list(data_sensor.split(","))
                    t = float(line[0])
                    value = float(line[1])
                    Logger.info(t)
                    x_raw.append(t)
                    ekg_raw.append(value)
                    # except ValueError:
                    #     pass
                except IOError:
                    Logger.info("Exception: IOerror")
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

    def get_value(self, _):
        self.plot.points = [(x_raw[i], j) for i, j in enumerate(ekg_raw)]

    def stop_reading(self):
        # Clock.unschedule(self.read_data)
        Clock.unschedule(self.get_value)
        if self.state_connection == 2:
            self.send_stream.write('1'.encode())
            self.state_connection = 1


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

    def build(self):
        return Backdrop()


if __name__ == '__main__':
    MainApp().run()
