from __future__ import print_function

import inspect
import cPickle as pickle
import matplotlib.pyplot as plt
import io
import networkx as nx

from story import Story, StoryError
from functools import partial

from kivy.config import Config
# disable multitouch from mouse
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, Metrics
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser
from kivy.core.image import Image as CoreImage
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty, StringProperty

Window.size = map(dp, (1280, 720))

# def inspect_wrap(f):
#     def wrapper(*args, **kwargs):
#         result = f(*args, **kwargs)
#         print(inspect.stack()[1])
#         return result
#     return wrapper
# 
# Label.__init__ = inspect_wrap(Label.__init__)

class AddActionPopup(Popup):
    pass

class HomeScreen(Screen):
    pass

class FileBrowserPopup(Popup):
    pass

class FileBrowserContent(BoxLayout):
    pass

class AddNodePopup(Popup):
    submit_btn_wid = ObjectProperty()
    node_name = StringProperty()

class EditScreen(Screen):
    dropdown_wid = ObjectProperty()
    node_info_wid = ObjectProperty()

    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.story = Story()

    def show_file_chooser(self):
        file_window = FileBrowserPopup(attach_to=self)
        file_window.board = self.ids['board']
        file_window.open()

    def check_current_file(self):
        board = self.ids['board']
        if board.current_file:
            board.save_story(board.current_file)
        else:
            self.show_file_chooser()

    def test_image(self):
        plt.rcParams['figure.dpi'] = 200
        plt.rcParams['figure.figsize'] = 16, 12
        plt.rcParams['figure.subplot.left'] = 0
        plt.rcParams['figure.subplot.right'] = 1
        plt.rcParams['figure.subplot.top'] = 1
        plt.rcParams['figure.subplot.bottom'] = 0
        plt.rcParams['figure.subplot.wspace'] = 0
        plt.rcParams['figure.subplot.hspace'] = 0

        g = nx.DiGraph()
        g.add_nodes_from(['box office', 'concessions', 'auditorium'])
        g.add_edge('box office', 'concessions')
        nx.draw_networkx(g, node_size=2000, font_size=dp(16), node_shape=',')

        curr_axes = plt.gca()
        curr_axes.axes.get_xaxis().set_visible(False)
        curr_axes.axes.get_yaxis().set_visible(False)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = CoreImage(buf, ext='png')
        
        return image
    
    def show_add_popup(self, button):
        # first select the button
        self.dropdown_wid.select(button.text)
        # then show the add popup
        p = AddNodePopup(attach_to=self)
        p.open()
        
        def show_info_callback(button):
            """Shows the node information in the sidebar
            """
            p.dismiss()
            node_info = self.node_info_wid
            node_info.clear_widgets()
            
            node_info.add_widget(Label(text='name:'))
            # TODO: allow node renaming?
            node_info.add_widget(TextInput(text=button.text, multiline=False))

            node_info.add_widget(Label(text='actions:'))
            node_info.add_widget(Button(text='edit actions...'))

        def add_callback(button):
            """Add the node to the story and update the dropdown menu
            """
            node_name = p.node_name
            self.story.add_node(node_name)
            print(self.story.nodes())
            p.dismiss()

            # update the dropdown menu
            b = Button(text=node_name, size_hint_y=None, height=dp(30)) 
            b.bind(on_release=show_info_callback)
            self.dropdown_wid.add_widget(b)
        p.submit_btn_wid.bind(on_release=add_callback)



class StoryboardApp(App):

    def build(self):
        sm = ScreenManager() # TODO: transitions
        # sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(EditScreen(name='edit'))
        return sm

if __name__ == '__main__':
    # print('dpi: %f' % Metrics.dpi)
    StoryboardApp().run()
