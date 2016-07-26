from __future__ import print_function

import inspect

from kivy.config import Config
# disable multitouch from mouse
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, Metrics
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# Builder.load_file("storyboard.kv")
Window.size = map(dp, (1280, 720))

# def inspect_wrap(f):
#     def wrapper(*args, **kwargs):
#         result = f(*args, **kwargs)
#         print(inspect.stack()[1])
#         return result
#     return wrapper
# 
# Label.__init__ = inspect_wrap(Label.__init__)

class AddNodeField(BoxLayout):
    pass

class AddNodeForm(BoxLayout):
    
    def __init__(self, **kwargs):
        super(AddNodeForm, self).__init__(**kwargs)
        self.fields = {}

class AddNodePopup(Popup):
    pass

class AddMenu(Bubble):
    pass

class AddMenuButton(BubbleButton):
    
    def on_press(self):
        if not self.last_touch.button == 'left':
            self.state = 'normal'

    def on_release(self):
        if self.last_touch.button == 'left':
            menu = self.parent.parent
            board = menu.board
            board.show_add_popup()
            
class EditNodeForm(BoxLayout):

    def __init__(self, **kwargs):
        super(EditNodeForm, self).__init__(**kwargs)
        self.fields = {}

class EditNodePopup(Popup):
    pass

class EditMenu(Bubble):
    pass

class EditMenuButton(BubbleButton):
    
    def on_press(self):
        if not self.last_touch.button == 'left':
            self.state = 'normal'

    def on_release(self):
        if self.last_touch.button == 'left':
            menu = self.parent.parent
            board = menu.board
            board.show_edit_popup()

class DeleteButton(EditMenuButton):

    def on_release(self):
        if self.last_touch.button == 'left':
            menu = self.parent.parent
            board = menu.board
            board.delete_node()

class StoryLabel(Label):

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == 'right':
            touch.grab(self)
            # print('grabbed')

    def on_touch_up(self, touch):
        # print('current:', touch.grab_current)
        # print('self:', self)
        if touch.grab_current is self:
            touch.ungrab(self)
            board = self.parent.parent
            touch.push()
            touch.apply_transform_2d(self.to_window)
            board.current_node = self.parent.proxy_ref
            board.show_edit(touch)
            touch.pop()
            # print('released')

class StoryNode(Scatter):
    pass

class Board(FloatLayout):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.add_menu = add_menu = AddMenu()
        add_menu.board = self.proxy_ref
        self.edit_menu = edit_menu = EditMenu()
        edit_menu.board = self.proxy_ref
        self.current_node = None

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            result = super(Board, self).on_touch_up(touch) # check children first
            # print('button: %s' % touch.button)
            # print('result:', result)
            # print(self.add_menu.collide_point(*touch.pos))
            if result:
                return None
            elif touch.button == 'left':
                # print('removing widget')
                self.remove_widget(self.add_menu)
                self.remove_widget(self.edit_menu)
            elif touch.button == 'right' and not self.add_menu.collide_point(*touch.pos):
                self.show_add(touch)
            return True

    def show_add(self, touch):
        self.add_menu.x = touch.x - self.add_menu.width / 2
        self.add_menu.y = touch.y
        self.add_menu.t_point = touch.pos
        if not self.add_menu.parent:
            self.add_widget(self.add_menu)

    def show_edit(self, touch):
        touch.apply_transform_2d(self.to_window)
        # print(touch.pos)
        # print('showing edit menu')
        self.edit_menu.x = touch.x - self.edit_menu.width / 2
        self.edit_menu.y = touch.y
        if not self.edit_menu.parent:
            self.add_widget(self.edit_menu)

    def show_add_popup(self):
        form = AddNodeForm()
        p = AddNodePopup(title='Add a story node',
                content=form,
                size_hint=(.4, .4))
        form.popup = p.proxy_ref
        form.board = self.proxy_ref
        p.open()

    def show_edit_popup(self):
        form = EditNodeForm()
        p = EditNodePopup(title='Edit a story node',
                content=form,
                size_hint=(.4, .4))
        form.popup = p.proxy_ref
        form.board = self.proxy_ref
        p.open()
    
    def add_node(self, name=None):
        n = StoryNode(do_scale=False, do_rotation=False)
        n.center = self.add_menu.t_point
        print(name)
        if name:
            n.ids['label'].text = name
        self.add_widget(n)

    def edit_node(self, name=None):
        node = self.current_node
        assert node, 'Current is none'
        if name:
            node.ids['label'].text = name
        self.current_node = None

    def delete_node(self):
        node = self.current_node
        assert node, 'Current is none'
        self.remove_widget(node)

class HomeScreen(Screen):
    pass

class EditScreen(Screen):
    pass

class StoryboardApp(App):

    def build(self):
        sm = ScreenManager() # TODO: transitions
        # sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(EditScreen(name='edit'))
        return sm

if __name__ == '__main__':
    # print('dpi: %f' % Metrics.dpi)
    StoryboardApp().run()
