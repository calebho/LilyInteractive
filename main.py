from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition

Builder.load_file("storyboard.kv")

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
