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

"""
Vector v = new Vector(drawRotateX, drawRotateY, 0);
float length = v.length();
v.normalize();
glRotatef(length, v.x, v.y, v.z);
"""

class Renderer(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        self.scene = ObjFile(resource_find("razoomnurbs.obj"))
        self.scene2 = ObjFile(resource_find("monkey.obj"))
        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        Clock.schedule_once(self.update_glsl, 1 / 60.)
        
        self._touches = []

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj

    def setup_scene(self):
        Color(1, 1, 1, 1)

        PushMatrix()
        Translate(0, 0, -3)
        self.rotx = Rotate(0, 1, 0, 0)
        self.roty = Rotate(0, 0, 1, 0)
        self.scale = Scale(1)
        m = self.scene.objects.values()[0]
        UpdateNormalMatrix()
        SetState(
                Kd=[0.9529, 0.0000, 0.0000],
                Ka=[0.9529, 0.0000, 0.0000],
                Ks=[0.3500, 0.3500, 0.3500],
                Ns=32.0,
                Tr=1.0
            )
        self.mesh = Mesh(
            vertices=m.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
        )
        m2 = self.scene2.objects.values()[0]
        self.test_mat = SetState(
                Kd=[0.4235, 0.0314, 0.5333],
                Ka=[0.4235, 0.0314, 0.5333],
                Ks=[0.3500, 0.3500, 0.3500],
                Ns=16.0,
                Tr=1.0
            )
        Mesh(
            vertices=m2.vertices,
            indices=m2.indices,
            fmt=m2.vertex_format,
            mode='triangles',
        )
        PopMatrix()
        
    def define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360
        y_angle = -1*(touch.dy/self.height)*360
        return x_angle, y_angle
    
    def on_touch_down(self, touch):
        self.update_glsl()
        self.test_mat['Tr'] -= 0.1
        if self.test_mat['Tr'] < 0:
            self.test_mat['Tr'] = 1
        touch.grab(self)
        self._touches.append(touch)
        
    def on_touch_up(self, touch): 
        touch.ungrab(self)
        self._touches.remove(touch)
        
    
    def on_touch_move(self, touch): 
        #Logger.debug("dx: %s, dy: %s. Widget: (%s, %s)" % (touch.dx, touch.dy, self.width, self.height))

        self.update_glsl()
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
                # here do just rotation        
                ax, ay = self.define_rotate_angle(touch)
                
                self.roty.angle += ax
                self.rotx.angle += ay

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
                    scale = SCALE_FACTOR
                    Logger.debug('Scale up')
                elif new_distance == old_distance:
                    scale = 0
                else:
                    scale = -1*SCALE_FACTOR
                    Logger.debug('Scale down')
                    
                xyz = self.scale.xyz
                
                if scale:
                    self.scale.xyz = tuple(p + scale for p in xyz)
        
        
        

class RendererApp(App):
    def build(self):

        return Renderer()

if __name__ == "__main__":
    RendererApp().run()
