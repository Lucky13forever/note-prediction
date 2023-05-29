import kivy
import os
import json
from os import listdir
from os.path import isfile, join
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FloatLayout
from note_recognition.note_recognition import run_basic_prediction
from note_recognition.utils import transform_notes_to_tab
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.lang import Builder

Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '800')

saved_tabs = dict()
current_tabs = None

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

    def select_file(self):
        from plyer import filechooser
        filechooser.open_file(on_selection = self.selected)

    def selected(self, selection):
        print("Path is ", selection[0])
        tabs = run_basic_prediction(selection[0])
        print("\n" * 2)
        print(tabs)
        print(self.ids)
        self.ids.label_tab.text = tabs
        global current_tabs
        current_tabs = tabs

    def show_popup(self):
        show = MyPopup()
        popupWindow = Popup(title="How tould you like yo name this tab?", content=show, size_hint=(None,None), size=(400, 400))
        show.set_window(popupWindow)
        popupWindow.open()

class SecondWindow(Screen):

    def on_enter(self, *args):
        super().on_enter(*args)
        self.add_label('Hello, world!')

    def add_label(self, text):
        label = Label(text=text, size_hint_y=None, height=40)
        self.ids['box_layout'].add_widget(label)

class WindowManager(ScreenManager):
    pass


class MyPopup(FloatLayout):

    def dismiss_popup(self):
        self.window.dismiss()

    def set_window(self, window):
        self.window = window

    def save_tab(self):
        self.save_tab_in_file(self.ids.tab_name.text, current_tabs)
        self.dismiss_popup()

    def give_file_name(self, path):
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        return f"tab{len(onlyfiles) + 1}"


    def save_tab_in_file(self, name, content):
        dir = os.path.dirname(os.path.realpath(__file__)) + "/saved"
        with open(f"{dir}/{self.give_file_name(dir)}.json", "w") as file:
            file.write(json.dumps({"name": name, "content": content}))


kv = Builder.load_file("./tabsonspot.kv")

class TabsOnSpot(App):

    def build(self):
        return kv

if __name__ == '__main__':
    TabsOnSpot().run()
