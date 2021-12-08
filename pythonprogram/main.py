import serial
from threading import Thread
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock


def serialsensor():
    ser = serial.Serial(port="COM5", baudrate=115200, timeout=1)
    ser.reset_input_buffer()
    global ekg
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode().rstrip()
            value = int(line)
            ekg.append(value)
            if len(ekg) >= 5000:
                ekg = []
            # print(value)


class MainApp(App):

    def build(self):
        return MainGrid()


class MainGrid(BoxLayout):

    zoom = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.zoom = 1
        self.graph = Graph(border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           y_ticks_major=50,
                           x_ticks_major=500,
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=5000,
                           ymin=-10, ymax=300,
                           draw_border=True,
                           x_grid_label=True, y_grid_label=True)

        self.plot = MeshLinePlot(color=[1, 1, 0, 1])
        self.graph.add_plot(self.plot)
        self.ids.modulation.add_widget(self.graph)

    def start(self):
        Clock.schedule_interval(self.get_value, 0.001)

    def stop(self):
        Clock.unschedule(self.get_value)

    def get_value(self, _):
        self.plot.points = [(i, j / 5) for i, j in enumerate(ekg)]

    def update_zoom(self, value):
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            # self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            # self.graph.x_ticks_major *= 2


if __name__ == '__main__':
    ekg = []
    get_sensor_thread = Thread(target=serialsensor)
    get_sensor_thread.daemon = True
    get_sensor_thread.start()
    MainApp().run()
