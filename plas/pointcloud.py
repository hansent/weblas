import numpy as np

class PointCloud:
    def __init__(self):
        self.schema = self.get_schema()
    
    def __len__(self):
        return self.num_points
        
    def get_schema(self):
        pass

    def get_bounds(self):
        pass    
    bounds = property(lambda x:x.get_bounds())
    
    def get_num_points(self):
        return None
    num_points = property(lambda x:x.get_num_points())
    
    def get_offsets(self):
        dims = ["X", "Y", "Z"]
        
        offsets = {}
        
        for d in dims:
            try:
                o = self.schema[d].offset
                o = float(o)
                offsets[d] = o
            except AttributeError:
                pass
        

        
        try:
            offset_x = offsets['X']
        except KeyError:
            offset_x = 0.0

        try:
            offset_y = offsets['Y']
        except KeyError:
            offset_y = 0.0

        try:
            offset_z = offsets['Z']
        except KeyError:
            offset_z = 0.0

        return np.array((offset_x, offset_y, offset_z))
        
    offsets = property(get_offsets)

    def get_scales(self):
        dims = ["X", "Y", "Z"]
        
        scales = {}
        
        for d in dims:
            try:
                o = self.schema[d].scale
                o = float(o)
                scales[d] = o
            except AttributeError:
                pass

        try:
            scale_x = scales['X']
        except KeyError:
            scale_x = 1.0

        try:
            scale_y = scales['Y']
        except KeyError:
            scale_y = 1.0

        try:
            scale_z = scales['Z']
        except KeyError:
            scale_z = 1.0
        
        return np.array((scale_x, scale_y, scale_z))
    scales = property(get_scales)
