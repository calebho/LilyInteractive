import pyglet
import threading
import time

talk = False

def run_avatar():
    animation = pyglet.resource.animation("AvatarGifs/idle1.gif")
    sprite = pyglet.sprite.Sprite(animation)
   
            
    # create a window and set it to the image size
    win = pyglet.window.Window(width=sprite.width, height=sprite.height)
    win.set_location(0,20)
    # set window background color = r, g, b, alpha
    # each value goes from 0.0 to 1.0
    white = 1, 1, 1, 1
    pyglet.gl.glClearColor(*white)              
    @win.event
    def on_draw():
        win.clear()
        sprite.draw()
    @win.event
    def on_mouse_press(x,y, button, modifiers):
        global talk
        if not talk:
            talk = True
            animation2=pyglet.resource.animation("AvatarGifs/talk1.gif")
        else:
            talk = False
            animation2=pyglet.resource.animation("AvatarGifs/idle1.gif")
        sprite.image = animation2
        on_draw()
    pyglet.app.run()
        
        



