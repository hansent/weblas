import numpy as np

class Bounds(object):
    def __init__(self,  minx=0.0, 
                        miny=0.0, 
                        minz=0.0, 
                        maxx=0.0, 
                        maxy=0.0, 
                        maxz=0.0, 
                        *args, 
                        **kwargs):
        self.min = np.array((minx, miny, minz))
        self.max = np.array((maxx, maxy, maxz))
    
    def set_minx(self, value):
        self.min[0] = value
    def get_minx(self):
        return self.min[0]
    minx = property(get_minx, set_minx)

    def set_miny(self, value):
        self.min[1] = value
    def get_miny(self):
        return self.min[1]
    miny = property(get_miny, set_miny)

    def set_minz(self, value):
        self.min[2] = value
    def get_minz(self):
        return self.min[2]
    minz = property(get_minz, set_minz)

    def set_maxx(self, value):
        self.max[0] = value
    def get_maxx(self):
        return self.max[0]
    maxx = property(get_maxx, set_maxx)


    def set_maxy(self, value):
        self.max[1] = value
    def get_maxy(self):
        return self.max[1]
    maxy = property(get_maxy, set_maxy)


    def set_maxz(self, value):
        self.max[2] = value
    def get_maxz(self):
        return self.max[2]
    maxz = property(get_maxz, set_maxz)
        
    
    def __str__(self):
        output = ''
        output += "<bounds.Bounds object at '0x%x' with min(%.2f, %.2f, %.2f) max(%.2f, %.2f, %.2f)>" % (id(self), self.minx, self.miny, self.minz, self.maxx, self.maxy, self.maxz)
        return output
    
    def isvalid(self):
        for i in range(len(self.min)):
            if self.min[i] > self.max[i]:
                return False
        return True
if __name__ == '__main__':
    b = Bounds()
    b.minx = -93.000
    b.maxx = -92.342
    b.miny = 42.00
    b.maxy = 42.53
    b.minz = 1034.41
    b.maxz = 1035.32
    
    print b
    print b.isvalid()