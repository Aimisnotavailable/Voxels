from settings import *

class ShaderProgram:
    def __init__(self, engine):
        self.engine = engine
        self.ctx = engine.ctx
        self.player = engine.player
        # ------------- shaders -----------------#
        self.chunk = self.get_program(shader_name='chunk')
        self.set_uniforms_on_init()
    
    def set_uniforms_on_init(self):
        self.chunk['m_proj'].write(self.player.m_proj)
        self.chunk['m_model'].write(glm.mat4())
        self.chunk['u_texture_0'] = 0
        
    def update(self):
        self.chunk['m_view'].write(self.player.m_view)

    def get_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert', 'r') as f:
            vertex_shader = f.read()
        with open(f'shaders/{shader_name}.frag', 'r') as f:
            fragment_shader = f.read()
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program