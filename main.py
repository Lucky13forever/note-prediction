import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FloatLayout
from note_recognition.note_recognition import run_basic_prediction
from note_recognition.utils import transform_notes_to_tab

kivy.require('1.9.0')

class MyRoot(FloatLayout):

    def __init__(self):
        super(MyRoot, self).__init__()

    def select_file(self):
        from plyer import filechooser
        filechooser.open_file(on_selection = self.selected)

    def selected(self, selection):
        print("Path is ", selection[0])
        # tabs = run_basic_prediction(selection[0])
        print("\n" * 2)
        # print(tabs)
        # self.ids.label_tab.text = tabs

    # we will first display 10 notes per tab



class TabsOnSpot(App):

    def build(self):
       return MyRoot()

obj = TabsOnSpot()
obj.run()
