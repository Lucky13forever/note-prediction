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
from kivy.properties import StringProperty


Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '800')

saved_tabs = []
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
        self.contor = 0
        self.ids['box_layout'].clear_widgets()
        self.add_labels()

    def add_labels(self):
        dir = os.path.dirname(os.path.realpath(__file__)) + "/saved/"
        onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]

        global saved_tabs
        saved_tabs = []
        for file_name in onlyfiles:
            with open(dir + file_name, "r") as file:
                data = json.loads(file.read())
                saved_tabs.append(data["content"])
                self.contor += 1
                label = ClickableLabel(text=str(self.contor) + ". " + data["name"], size_hint_y=None, height=40, font_size=20)
                label.bind(on_release=self.on_label_click)
                self.ids['box_layout'].add_widget(label, index=0)

    def on_label_click(self, label):
        screen_manager = App.get_running_app().root
        third_screen = screen_manager.get_screen('third')
        third_screen.tabs_title = label.text.split(". ")[1]
        third_screen.tabs_content = saved_tabs[int(label.text.split(". ")[0]) - 1]
        screen_manager.current = 'third'  # switch to the third screen
        App.get_running_app().root.current = "third"

class ThirdWindow(Screen):
    tabs_title = StringProperty('')
    tabs_content = StringProperty('')

    def on_enter(self, *args):
        super().on_enter(*args)
        self.ids['title_tab'].text = self.tabs_title
        self.ids['title_content'].text = self.tabs_content

from kivy.uix.button import Button

class ClickableLabel(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # makes button background transparent
        self.color = (1, 1, 1, 1)  # text color is black

    def on_release(self):
        print(f'The label "{self.text}" was clicked!')


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
            if content is None:
                content = "Empty"
            file.write(json.dumps({"name": name, "content": content}))


kv = Builder.load_file("./tabsonspot.kv")

class TabsOnSpot(App):

    def build(self):
        return kv

if __name__ == '__main__':
    TabsOnSpot().run()
