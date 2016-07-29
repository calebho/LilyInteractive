import pyglet 
import platform
if platform.system() == 'Windows':
    from win32api import GetSystemMetrics
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
elif platform.system() == 'Linux':
    import subprocess
    output = subprocess.check_output("xrandr  | grep \* | cut -d' ' -f4", shell=True)
    output = output.strip()
    w, h = map(int, output.split('x'))
else:
    raise RuntimeError('Unable to get screen resolution')

talk = False

def run_avatar():
    animation = pyglet.resource.animation("AvatarGifs/lily_idle.gif")
    sprite = pyglet.sprite.Sprite(animation)
    sprite.set_position((w - sprite.width)/2, (h - sprite.height)/2)
    #create a window and set it to fullscreen
    win = pyglet.window.Window(fullscreen = True)
    win.set_location(0,0)
    #set window background color = r, g, b, alpha
    #each value goes from 0.0 to 1.0
    background_color = 0.815, 0.87, 1, 1
    pyglet.gl.glClearColor(*background_color)              
    @win.event
    def on_draw():
        win.clear()
        sprite.draw()
    #avatar is switched from idle to talking mode by a simulated mouse press
    @win.event
    def on_mouse_press(x,y, button, modifiers):
        global talk
        if not talk:
            talk = True
            animation2=pyglet.resource.animation("AvatarGifs/lily_talking.gif")
        else:
            talk = False
            animation2=pyglet.resource.animation("AvatarGifs/lily_idle.gif")
        sprite.image = animation2
        on_draw()
    pyglet.app.run()

if __name__ == '__main__':
    run_avatar()
        
        




