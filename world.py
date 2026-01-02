from settings import *
from world_objects.chunk import Chunk
from voxel_handler import VoxelHandler
from world_data_handler import VoxelPacker, VoxelUnpacker


class World:
    def __init__(self, engine):
        self.engine = engine
        self.chunks = [None for _ in range(WORLD_VOL)]
        self.voxels = np.empty([WORLD_VOL, CHUNK_VOL], dtype='uint8')
        self.build_chunks()
        self.build_chunk_mesh()
        self.voxel_handler = VoxelHandler(self)

    def update(self):
        self.voxel_handler.update()

    def load_chunk_file(self):
        with open(CHUNK_FILE_BASE_DIR / Path(f'world{CHUNK_FILE_FORMAT}'), 'r+') as fp:
            packed_data = json.load(fp)
            unpacked_voxels_data = VoxelUnpacker().unpack(packed_data['voxels'])
            for x in range(WORLD_W):
                for y in range(WORLD_H):
                    for z in range(WORLD_D):
                        idx = x + WORLD_W * z + WORLD_AREA * y
                        chunk = Chunk(self, position=packed_data['chunk_pos'][idx])

                        chunk_voxels = unpacked_voxels_data[idx]
                        
                        self.chunks[idx] = chunk
                        self.voxels[idx] = chunk_voxels

                        chunk.voxels = self.voxels[idx]
                        if np.any(chunk_voxels):
                            chunk.is_empty = False
        # print(self.chunks[idx].voxels)

    def save_chunk_file(self):
        with open(CHUNK_FILE_BASE_DIR / Path(f'world{CHUNK_FILE_FORMAT}'), 'w+') as fp:
            pos_list = []
            for chunk in self.chunks:
                pos_list.append(chunk.position)
            voxel_data = VoxelPacker().pack_voxel_data(self.voxels.tolist())
            data = {'voxels' : voxel_data,
                    'chunk_pos' : pos_list}
            
            json.dump(data, fp, indent=2)

    def build_chunks(self):
        self.load_chunk_file()
        # for x in range(WORLD_W):
        #     for y in range(WORLD_H):
        #         for z in range(WORLD_D):
        #             chunk = Chunk(self, position=(x, y, z))

        #             chunk_index = x + WORLD_W * z + WORLD_AREA * y
        #             self.chunks[chunk_index] = chunk

        #             # put the chunk voxels in a separate array
        #             self.voxels[chunk_index] = chunk.build_voxels()

        #             # get pointer to voxels
        #             chunk.voxels = self.voxels[chunk_index]
        # self.save_chunk_file()

    def build_chunk_mesh(self):
        for chunk in self.chunks:
            chunk.build_mesh()

    def render(self):
        for chunk in self.chunks:
            chunk.render()
