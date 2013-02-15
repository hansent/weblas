            # f = laspy.file.File(filename)
            # self.minima = f.header.min
            # self.maxima = f.header.max
            # 
            # vx = f.x.astype(np.float32)
            # vy = f.y.astype(np.float32)
            # vz = f.z.astype(np.float32)
            # points = np.vstack((vx, vy, vz)).transpose()[0::100]
            # points = (points - self.minima) /10.0 #/ max(self.maxima)
            # self.points = points.ravel().astype(np.float32)
            # 
            # self.num_points = len(self.points)
            # self.item_size = self.points.dtype.itemsize
            # self.point_size = self.item_size * 3
            # self.buffer_size = self.point_size * self.num_points
            # self.chunk_size = self.point_size * 10000
            # self.offset = 0
            # 

import laspy.file

import pointcloud
import bounds

class LASFile(pointcloud.PointCloud):
    def __init__(self, filename, *args, **kwargs):
        self.f = laspy.file.File(filename)
        self.filename = filename
        pointcloud.PointCloud.__init__(self, *args, **kwargs)
    
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
    
    filename = './static/serpent.las'
    p = LASFile(filename)
        
    print p.bounds
    byte_size = sum([int(i.size) for i in p.schema])
    print byte_size
    print len(p)

    print p.offsets, p.scales

    