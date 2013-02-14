import numpy as np

class PointCloud:
    def __init__(self):
        self.schema = self.get_schema()

    def get_schema(self):
        pass

    def get_bounds(self):
        pass    
    bounds = property(lambda x:x.get_bounds())
    
    def get_num_points(self):
        return None
    num_points = property(lambda x:x.get_num_points())

