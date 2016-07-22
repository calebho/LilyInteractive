from __future__ import print_function

from kivy.config import Config
# disable multitouch from mouse
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter

Builder.load_file("storyboard.kv")

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
            n = StoryNode(do_scale=False, do_rotation=False)
            n.center = menu.t_point
            board.add_widget(n)


class StoryLabel(Label):
    pass

class StoryNode(Scatter):
    pass

class Board(FloatLayout):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.edit_menu = edit_menu = EditMenu()
        edit_menu.board = self.proxy_ref

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            super(Board, self).on_touch_up(touch) # check children first
            print('button: %s' % touch.button)
            print('result:', result)
            print(self.edit_menu.collide_point(*touch.pos))
            if touch.button == 'left':
                print('removing widget')
                self.remove_widget(self.edit_menu)
            elif touch.button == 'right' and not self.edit_menu.collide_point(*touch.pos):
                self.show_edit(touch)
            return True

    def show_edit(self, touch):
        self.edit_menu.x = touch.x - self.edit_menu.width / 2
        self.edit_menu.y = touch.y
        self.edit_menu.t_point = touch.pos
        if not self.edit_menu.parent:
            self.add_widget(self.edit_menu)

class HomeScreen(Screen):
    pass

class EditScreen(Screen):
    pass

sm = ScreenManager() # TODO: transitions
sm.add_widget(HomeScreen(name='home'))
sm.add_widget(EditScreen(name='edit'))

class StoryboardApp(App):

    def build(self):
        return sm

if __name__ == '__main__':
    StoryboardApp().run()
