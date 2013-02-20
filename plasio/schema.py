


class Dimension(object):
    def __init__(self):
        self.index = None

    def __cmp__(self, other):
        if not self.index and not other.index:
            raise Exception("Dimension does not have index specified!")
        if self.index > other.index:
            return 1
        if self.index < other.index:
            return -1
        if self.index == other.index:
            return 0
    
    def __str__(self):
        output = ''
        for name in self.__dict__:
            v = self.__dict__[name]
            output = output + '%s:%s\n' % (name, v)
        return output
        

class Schema(object):
    def __init__(self):
        self.dimensions = {}
        
    def __str__(self):
        output = ''
        output += "<schema.Schema object at '0x%x' with %d dimensions>" % (id(self), len(self.dimensions))
        return output
        
    def __iter__(self):
        dims = []
        for dim in self.dimensions:
            dims.append(self.dimensions[dim])
        dims.sort()
        for dim in dims:
            yield dim
    
    def __getitem__(self, name):
        return self.dimensions[name]
    
    def append(self, dimension):
        if self.dimensions.has_key(dimension.name):
            raise Exception("Dimension with name '%s' already exists on this schema!" % dimension.name)
        self.dimensions[dimension.name] = dimension
        
    def remove(self, name):
        del self.dimensions[name]

    def get_np_fmt(self):
        import numpy as np
        fmt = []
        for dim in self:
            f = dim.np_fmt
            fmt.append(f.descr[0])
        return np.dtype(fmt)
    np_fmt = property(get_np_fmt)