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
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.filechooser import FileChooser
from kivy.core.image import Image as CoreImage
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty, StringProperty

Window.size = map(dp, (1280, 720))

# matplotlib parameters
plt.rcParams['figure.dpi'] = 200
plt.rcParams['figure.figsize'] = 16, 12
plt.rcParams['figure.subplot.left'] = 0
plt.rcParams['figure.subplot.right'] = 1
plt.rcParams['figure.subplot.top'] = 1
plt.rcParams['figure.subplot.bottom'] = 0
plt.rcParams['figure.subplot.wspace'] = 0
plt.rcParams['figure.subplot.hspace'] = 0

class AddActionPopup(Popup):
    pass

class HomeScreen(Screen):
    pass

class FileBrowserPopup(Popup):
    pass

class FileBrowserContent(BoxLayout):
    pass

class AddEdgePopup(Popup):
    node_list = ObjectProperty()
    save_btn = ObjectProperty()

class AddNodePopup(Popup):
    submit_btn_wid = ObjectProperty()
    node_name = StringProperty()

class AddActionPopup(Popup):
    actions_list_wid = ObjectProperty()
    add_action_btn_wid = ObjectProperty()
    save_btn = ObjectProperty()
    cancel_btn = ObjectProperty()

    def __init__(self, existing_actions=None, **kwargs):
        super(AddActionPopup, self).__init__(**kwargs)
        self.actions_list_wid.bind(minimum_height=self.actions_list_wid.setter('height'))
        self._actions_temp = None
        self.actions_temp = existing_actions

    @property
    def actions_temp(self):
        return self._actions_temp

    @actions_temp.setter
    def actions_temp(self, actions):
        self._actions_temp = []
        if actions:
            for action in actions:
                a = Action()
                a.action_type = action['type']
                a.type_button_wid.text = action['type']
                a.parameters = action['kwargs']
                self.add_action(a)

    def add_action(self, action):
        def move_action_up(button):
            for i, a in enumerate(self.actions_temp[:]):
                if action is a and i > 0:
                    self.actions_temp[i-1], self.actions_temp[i] =\
                            self.actions_temp[i], self.actions_temp[i-1]
            self.render_actions()

        def move_action_down(button):
            for i, a in enumerate(self.actions_temp[:]):
                if action is a and i < len(self.actions_temp) - 1:
                    self.actions_temp[i], self.actions_temp[i+1] =\
                            self.actions_temp[i+1], self.actions_temp[i]
            self.render_actions()
            
        action.move_up_btn.bind(on_release=move_action_up)
        action.move_down_btn.bind(on_release=move_action_down)
        self.actions_list_wid.add_widget(action)
        self.actions_temp.append(action)

    def render_actions(self):
        self.actions_list_wid.clear_widgets()
        for action in self.actions_temp:
            self.actions_list_wid.add_widget(action)

class Action(BoxLayout):
    action_type = StringProperty()
    type_button_wid = ObjectProperty()
    set_param_btn_wid = ObjectProperty()
    move_up_btn = ObjectProperty()
    move_down_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super(Action, self).__init__(**kwargs)
        self.init_type_dropdown()
        self.parameters = None # dict of parameters to the corresponding action

    def init_type_dropdown(self):
        d = DropDown()
        action_types = ['say', 'listen', 'play']
        for action_type in action_types:
            b = Button(text=action_type, size_hint_y=None, height=dp(30))

            def action_select_callback(button):
                d.select(button.text)
                # reset parameters when changing action type
                if self.action_type != button.text:
                    self.parameters = None
                self.action_type = button.text
            b.bind(on_release=action_select_callback)
            d.add_widget(b)

        d.bind(on_select=\
                lambda instance, text: setattr(self.type_button_wid, 'text', text))
        self.type_button_wid.bind(on_release=d.open)

    def get_parameters(self):
        btn = self.set_param_btn_wid
        g = GridLayout(cols=2)
        param_temp = {}
        if self.action_type == 'say':
            g.add_widget(Label(text='message'))
            t = TextInput()
            if self.parameters:
                try:
                    t.text = self.parameters['message']
                except KeyError: 
                    pass
            t.bind(text=lambda _, value: param_temp.update({'message': value}))
            g.add_widget(t)
        elif self.action_type == 'listen':
            g.add_widget(Label(text='intent'))
            t = TextInput(multiline=False)
            if self.parameters:
                try:
                    t.text = self.parameters['intent']
                except KeyError:
                    pass
            t.bind(text=lambda _, value: param_temp.update({'intent': value}))
            g.add_widget(t)
        elif self.action_type == 'play':
            g.add_widget(Label(text='file path'))
            t = TextInput(multiline=False)
            if self.parameters:
                try:
                    t.text = self.parameters['filename']
                except KeyError:
                    pass
            t.bind(text=lambda _, value: param_temp.update({'filename': value}))
            g.add_widget(t)
        else:
            return

        p = Popup(title='Set parameters', size_hint=(.5, .2))
        # btn.bind(on_release=p.open)

        def submit_callback(button):
            self.parameters = param_temp
            p.dismiss()

        submit_btn = Button(text='Submit')
        submit_btn.bind(on_release=submit_callback)
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_release=lambda _: p.dismiss())
        g.add_widget(submit_btn)
        g.add_widget(cancel_btn)
        p.content = g
        p.open()

class EditScreen(Screen):
    # dropdown_wid = ObjectProperty()
    dropdown_btn_wid = ObjectProperty()
    node_info_wid = ObjectProperty()
    refresh_btn = ObjectProperty()
    storyboard_wid = ObjectProperty()

    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.d = None
        self.init_node_select_dropdown()
        self.story = Story()
        self.current_node = None
        self.refresh_btn.bind(on_release=self.refresh_graph)

    def init_node_select_dropdown(self):
        self.d = d = DropDown()
        b = Button(text='Add a node...', size_hint_y=None, height=dp(30))
        b.bind(on_release=self.show_add_popup)
        d.add_widget(b)
        d.bind(on_select=lambda _, text: setattr(self.dropdown_btn_wid, 'text', text))
        self.dropdown_btn_wid.bind(on_release=d.open)

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

    def refresh_graph(self, button):
        g = self.story
        plt.clf()
        nx.draw_networkx(g, node_size=2000, font_size=dp(16), node_shape=',')

        curr_axes = plt.gca()
        curr_axes.axes.get_xaxis().set_visible(False)
        curr_axes.axes.get_yaxis().set_visible(False)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = CoreImage(buf, ext='png')
        
        self.storyboard_wid.texture = image.texture
    
    def show_add_popup(self, button):
        # show the add popup
        p = AddNodePopup(attach_to=self)
        p.open()
        
        def show_info_callback(button):
            """Shows the node information in the sidebar
            """
            self.current_node = button.text
            self.d.select(button.text)
            # p.dismiss()
            node_info = self.node_info_wid
            node_info.clear_widgets()
            
            node_info.add_widget(Label(text='name:'))
            # TODO: allow node renaming?
            node_info.add_widget(TextInput(text=button.text, multiline=False))

            node_info.add_widget(Label(text='actions:'))
            actions_b = Button(text='edit...')
            actions_b.bind(on_release=self.show_add_action_popup)
            node_info.add_widget(actions_b)

            node_info.add_widget(Label(text='destinations:'))
            dest_b = Button(text='edit...')
            dest_b.bind(on_release=self.show_add_dest_popup)
            node_info.add_widget(dest_b)

            node_info.add_widget(Label(text='origins:'))
            orig_b = Button(text='edit...')
            orig_b.bind(on_release=self.show_add_origin_popup)
            node_info.add_widget(orig_b)

        def add_callback(button):
            """Add the node to the story and update the dropdown menu
            """
            self.d.dismiss()
            node_name = p.node_name
            self.story.add_node(node_name)
            print(self.story.nodes())
            p.dismiss()

            # update the dropdown menu
            b = Button(text=node_name, size_hint_y=None, height=dp(30)) 
            b.bind(on_release=show_info_callback)
            self.d.add_widget(b)
        p.submit_btn_wid.bind(on_release=add_callback)

    def show_add_action_popup(self, button):
        p = AddActionPopup(existing_actions=self.story.get_actions(self.current_node),
                attach_to=self)
        p.open()
        def add_action_callback(button):
            a = Action()
            p.add_action(a)
            # p.actions_list_wid.add_widget(a)
            # p.actions_temp.append(a)

        def update_story(action):
            if action.action_type == 'say':
                self.story.add_say(self.current_node, **action.parameters)
            elif action.action_type == 'listen':
                self.story.add_listen(self.current_node, **action.parameters)
            elif action.action_type == 'play':
                self.story.add_play(self.current_node, **action.parameters)

        def save_callback(button):
            actions = p.actions_temp
            for action in actions:
                update_story(action)
            p.dismiss()

        p.add_action_btn_wid.bind(on_release=add_action_callback)
        p.save_btn.bind(on_release=save_callback)

    def show_add_dest_popup(self, button):
        p = AddEdgePopup(title='Add destinations')
        valid_dest = self.story.nodes()
        valid_dest.remove(self.current_node)
        for dest in valid_dest:
            b = ToggleButton(text=dest, size_hint_y=None, height=dp(30))
            if dest in self.story.neighbors(self.current_node):
                b.state = 'down'
            p.node_list.add_widget(b)
        p.node_list.add_widget(Widget())

        def save_callback(button):
            to_add = []
            to_remove = []
            for child in p.node_list.children:
                if isinstance(child, ToggleButton):
                    node_name = child.text
                    if child.state == 'down':
                        to_add.append(node_name)
                    else:
                        to_remove.append(node_name)
            for node in to_add:
                if node not in self.story.neighbors(self.current_node):
                    self.story.add_edge(self.current_node, node)
            for node in to_remove:
                if node in self.story.neighbors(self.current_node):
                    self.story.remove_edge(self.current_node, node)
            p.dismiss()
        p.save_btn.bind(on_release=save_callback)
        
        p.open()

    def show_add_origin_popup(self, button):
        p = AddEdgePopup(title='Add origins')
        valid_orig = self.story.nodes()
        valid_orig.remove(self.current_node)
        for orig in valid_orig:
            b = ToggleButton(text=orig, size_hint_y=None, height=dp(30))
            if orig in self.story.predecessors(self.current_node):
                b.state = 'down'
            p.node_list.add_widget(b)
        p.node_list.add_widget(Widget())

        def save_callback(button):
            to_add = []
            to_remove = []
            for child in p.node_list.children:
                if isinstance(child, ToggleButton):
                    node_name = child.text
                    if child.state == 'down':
                        to_add.append(node_name)
                    else:
                        to_remove.append(node_name)
            for node in to_add:
                if node not in self.story.predecessors(self.current_node):
                    self.story.add_edge(node, self.current_node)
            for node in to_remove:
                if node in self.story.predecessors(self.current_node):
                    self.story.remove_edge(node, self.current_node)
            p.dismiss()
        p.save_btn.bind(on_release=save_callback)
        
        p.open()

class StoryboardApp(App):

    def build(self):
        sm = ScreenManager() # TODO: transitions
        # sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(EditScreen(name='edit'))
        return sm

if __name__ == '__main__':
    # print('dpi: %f' % Metrics.dpi)
    StoryboardApp().run()
