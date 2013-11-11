import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from objloader import ObjFile
from kivy.logger import Logger
from kivy.vector import Vector
from kivy.core.image import Image


class Renderer(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        self.scene = ObjFile(resource_find("orion.obj"))
        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        self.camera_translate = [0, 0, -0.67]
        self.camera_ax = 0
        self.camera_ay = 0
        Clock.schedule_once(self.update_glsl, 1 / 60.)    
        
        self._touches = []

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        asp = asp*0.3
        proj = Matrix()
        mat = Matrix()
        mat = mat.look_at(0, 0, self.camera_translate[2], 0, 0, -3, 0, 1, 0)
        proj = proj.view_clip(-asp, asp, -.3, .3, 1, 100, 1)
        
        self.canvas['projection_mat'] = proj
        self.canvas['modelview_mat'] = mat

    def setup_scene(self):
        texture = Image('orion.png').texture
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, -4)
        self.rotx = Rotate(0, 0, 1, 0)
        self.roty = Rotate(0, 1, 0, 0)
        #self.scale = Scale(0.6)
        m = self.scene.objects.values()[0]
        UpdateNormalMatrix()
        self.mesh = Mesh(
            vertices=m.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
            texture=texture,
        )
        PopMatrix()
        
    def define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360
        y_angle = -1*(touch.dy/self.height)*360
        return x_angle, y_angle
    
    def on_touch_down(self, touch):
        touch.grab(self)
        self._touches.append(touch)
        
    def on_touch_up(self, touch):
        touch.ungrab(self)
        self._touches.remove(touch)
        
    
    def on_touch_move(self, touch): 
        #Logger.debug("dx: %s, dy: %s. Widget: (%s, %s)" % (touch.dx, touch.dy, self.width, self.height))
        #self.update_glsl()
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                # here do just rotation        
                ax, ay = self.define_rotate_angle(touch)
                
                
                self.rotx.angle += ax
                self.roty.angle += ay
                
                #ax, ay = math.radians(ax), math.radians(ay)
                

            elif len(self._touches) == 2: # scaling here
                #use two touches to determine do we need scal
                touch1, touch2 = self._touches 
                old_pos1 = (touch1.x - touch1.dx, touch1.y - touch1.dy)
                old_pos2 = (touch2.x - touch2.dx, touch2.y - touch2.dy)
                
                old_dx = old_pos1[0] - old_pos2[0]
                old_dy = old_pos1[1] - old_pos2[1]
                
                old_distance = (old_dx*old_dx + old_dy*old_dy)
                Logger.debug('Old distance: %s' % old_distance)
                
                new_dx = touch1.x - touch2.x
                new_dy = touch1.y - touch2.y
                
                new_distance = (new_dx*new_dx + new_dy*new_dy)
                
                Logger.debug('New distance: %s' % new_distance)
                SCALE_FACTOR = 0.01
                
                if new_distance > old_distance: 
                    scale = -1*SCALE_FACTOR
                    Logger.debug('Scale up')
                elif new_distance == old_distance:
                    scale = 0
                else:
                    scale = SCALE_FACTOR
                    Logger.debug('Scale down')
                
                if scale:
                    self.camera_translate[2] += scale
                    print scale, self.camera_translate
            self.update_glsl()


class RendererApp(App):
    def build(self):

        return Renderer()

if __name__ == "__main__":
    RendererApp().run()
