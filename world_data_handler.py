from settings import *
class VoxelPacker:
    def to_str(self, num: int) -> str:
        # map 0..61 -> '0'-'9', 'a'-'z', 'A'-'Z'
        if 0 <= num <= 9:
            return chr(ord('0') + num)
        if 10 <= num <= 35:
            return chr(ord('a') + (num - 10))
        if 36 <= num <= 61:
            return chr(ord('A') + (num - 36))
        raise ValueError("to_str: num out of range 0..61")

    def encode_count_base62(self, count: int) -> str:
        if count <= 0:
            return self.to_str(0)
        digits = []
        while count > 0:
            digits.append(self.to_str(count % 62))
            count //= 62
        digits.reverse()
        return ''.join(digits)

    def pack_voxel_data(self, voxels):

        packed_voxels = []

        for chunk_voxels in voxels:
            if not chunk_voxels:
                packed_voxels.append('')  # keep chunk alignment
                continue

            curr_voxel_id = chunk_voxels[0]
            counter = 1
            parts = []

            for voxel in chunk_voxels[1:]:
                if voxel == curr_voxel_id:
                    counter += 1
                else:
                    parts.append(f';{self.encode_count_base62(counter)}-{curr_voxel_id}')
                    curr_voxel_id = voxel
                    counter = 1

            # flush last run for this chunk
            parts.append(f';{self.encode_count_base62(counter)}-{curr_voxel_id}')
            packed_voxels.append(''.join(parts))

        return packed_voxels

class VoxelUnpacker:
    
    def _digit_from_char(self, ch: str) -> int:
        if '0' <= ch <= '9':
            return ord(ch) - ord('0')
        if 'a' <= ch <= 'z':
            return ord(ch) - ord('a') + 10
        if 'A' <= ch <= 'Z':
            return ord(ch) - ord('A') + 36
        raise ValueError(f"Invalid base62 digit: {ch}")

    def decode_count_base62(self, s: str) -> int:

        if s == '':
            return 0
        value = 0
        for ch in s:
            value = value * 62 + self._digit_from_char(ch)
        return value
    
    def unpack(self, voxels_data):
        world_voxels = []
        for chunk_voxels in voxels_data:
            parts = []
            for voxel_data in chunk_voxels.split(';')[1:]:
                voxel_count, voxel_id = voxel_data.split('-')
                count = self.decode_count_base62(voxel_count)
                parts.append(np.full(count, int(voxel_id), dtype=np.uint8))
            chunk = np.concatenate(parts) if parts else np.empty(0, dtype=np.uint8)
            world_voxels.append(chunk)
        return np.array(world_voxels, dtype=np.uint8)

    
# with open(CHUNK_FILE_BASE_DIR / Path(f'world{CHUNK_FILE_FORMAT}'), 'r+') as fp:
#     packed_data = json.load(fp)
#     print(len(VoxelUnpacker().unpack(packed_data['voxels'])))
