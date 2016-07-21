from __future__ import print_function

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter

Builder.load_file("storyboard.kv")

class edit_menu(Bubble):
    pass

class StoryLabel(Label):
    pass

class StoryNode(Scatter):
    pass

class Board(FloatLayout):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # check whether we've collided with a widget
            result = super(Board, self).on_touch_down(touch)
            # if not, add a node and stop the touch event propagation
            if not result:
                n = StoryNode(do_scale=False, do_rotation=False)
                n.center = touch.pos
                self.add_widget(n)
                return True

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
