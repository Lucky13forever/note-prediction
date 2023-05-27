import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FloatLayout
from note_recognition.note_recognition import run_basic_prediction
from note_recognition.utils import transform_notes_to_tab
from kivy.config import Config
from kivy.uix.popup import Popup

kivy.require('1.9.0')
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '800')

saved_tabs = dict()
current_tabs = None

class MyRoot(FloatLayout):

    def __init__(self):
        super(MyRoot, self).__init__()

    def select_file(self):
        from plyer import filechooser
        filechooser.open_file(on_selection = self.selected)

    def selected(self, selection):
        print("Path is ", selection[0])
        tabs = run_basic_prediction(selection[0])
        print("\n" * 2)
        print(tabs)
        self.ids.label_tab.text = tabs
        global current_tabs
        current_tabs = tabs

    def show_popup(self):
        show = MyPopup()
        popupWindow = Popup(title="How tould you like yo name this tab?", content=show, size_hint=(None,None), size=(400, 400))
        show.set_window(popupWindow)
        popupWindow.open()

class MyPopup(FloatLayout):

    def dismiss_popup(self):
        self.window.dismiss()

    def set_window(self, window):
        self.window = window

    def save_tab(self):
        # print("save tab ", self.ids.tab_name.text)
        saved_tabs[self.ids.tab_name.text] = current_tabs
        print(saved_tabs)
        self.dismiss_popup()

class TabsOnSpot(App):

    def build(self):
       return MyRoot()



obj = TabsOnSpot()
obj.run()
