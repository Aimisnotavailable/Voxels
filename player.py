import pygame as pg
from camera import Camera
from settings import *


class Player(Camera):
    def __init__(self, engine, position=PLAYER_POS, yaw=-90, pitch=0):
        self.engine = engine
        self.p_speed = PLAYER_SPEED
        super().__init__(position, yaw, pitch)

    def update(self):
        self.keyboard_control()
        self.mouse_control()
        super().update()

    def handle_event(self, event):
        # adding and removing voxels with clicks
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.engine.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        self.p_speed = min(MAX_PLAYER_SPEED, self.p_speed + 0.001)
        vel = self.p_speed * self.engine.delta_time

        if key_state[pg.K_w]:
            self.move_forward(vel)
        if key_state[pg.K_s]:
            self.move_back(vel)
        if key_state[pg.K_d]:
            self.move_right(vel)
        if key_state[pg.K_a]:
            self.move_left(vel)
        if key_state[pg.K_q]:
            self.move_up(vel)
        if key_state[pg.K_e]:
            self.move_down(vel)
        
        if not (key_state[pg.K_w] or key_state[pg.K_s] or
                key_state[pg.K_a] or key_state[pg.K_d] or
                key_state[pg.K_q] or key_state[pg.K_e]):
            self.p_speed = PLAYER_SPEED
