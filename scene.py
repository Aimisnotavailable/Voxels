from settings import *
from world import World
from world_objects.voxel_marker import VoxelMarker

class Scene:

    def __init__(self, engine):
        self.engine = engine
        self.world = World(self.engine)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
    
    def update(self):
        self.world.update()
        self.voxel_marker.update()
        
    def render(self):
        self.world.render()
        self.voxel_marker.render()