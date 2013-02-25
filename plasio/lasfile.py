import numpy as np

import laspy.file

import pointcloud
import bounds

class LASFile(pointcloud.PointCloud):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.chunk_size = kwargs.get('chunk_size', 10000)
        self.offset = 0

        self.f = f = laspy.file.File(self.filename)


        self.normalize()
        self.points = self.process_point_data(f.x, f.y, f.z)
        pointcloud.PointCloud.__init__(self, *args, **kwargs)


    def normalize(self):
        b = self.bounds
        self.extents = [(b.max[i]-b.min[i]) for i in range(3)]
        self.scale_factor = 1.0/max(self.extents)
        self.center = [0.5*self.extents[i] for i in range(3)]

    def process_point_data(self, x, y, z):
        vx = x.astype(np.float32)
        vy = y.astype(np.float32)
        vz = z.astype(np.float32)

        #interleave as list of vec3's
        points = np.vstack((vx, vy, vz)).transpose()

        #normalize to in16
        b = self.bounds
        points = points - b.min
        points = points * self.scale_factor *  (2**16 -1)
        points = points.ravel()
        return (points ).astype(np.uint16)


    def next(self):
        if self.offset >= len(self.points):
            raise StopIteration
        data = np.getbuffer(self.points, self.offset, self.chunk_size)
        self.offset = self.offset + self.chunk_size
        return data

    def __iter__(self):
        return self

    def get_bounds(self):
        return bounds.Bounds(*tuple(self.f.header.min + self.f.header.max))

    def get_num_points(self):
        return len(self.f.header)

    def get_schema(self):
        import schema
        s = schema.Schema()
        i = 0
        for spec in self.f.point_format:
            d = schema.Dimension()
            d.size = spec.length
            d.name = spec.name
            d.index = i
            d.np_fmt = spec.np_fmt
            s.append(d)
            i = i + 1

        s['X'].scale = self.f.header.scale[0]
        s['Y'].scale = self.f.header.scale[1]
        s['Z'].scale = self.f.header.scale[2]

        s['X'].offset = self.f.header.offset[0]
        s['Y'].offset = self.f.header.offset[1]
        s['Z'].offset = self.f.header.offset[2]

        return s


if __name__ == '__main__':

    filename = '../static/serpent.las'
    p = LASFile(filename)

    print p.bounds
    byte_size = sum([int(i.size) for i in p.schema])
    print byte_size
    print len(p)

    print p.offsets, p.scales


