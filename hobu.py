import psycopg2
import numpy as np

class Dimension:
    def __init__(self, element):
        # element.tag is something like 
        # '{http://pointcloud.org/schemas/PC/1.1}dimension'
        # extract the name space so we 
        ns = element.tag.replace('dimension', '')
        for attribute in element:
            self.__dict__[attribute.tag.replace(ns,'')] = attribute.text
        self.index = None
    # def __eq__(self, other):
    #     return self.name == other.name
    
    def __cmp__(self, other):
        if not self.index and not other.index:
            raise Exception("Dimension does not have index specified!")
        if self.index > other.index:
            return 1
        if self.index < other.index:
            return -1
        if self.index == other.index:
            return 0

class Schema:
    def __init__(self):
        self.dimensions = {}
    def __iter__(self):
        for dim in self.dimensions:
            yield self.dimensions[dim]
    
    def __getitem__(self, name):
        return self.dimensions[name]
    
    def append(self, dimension):
        if self.dimensions.has_key(dimension.name):
            raise Exception("Dimension with name '%s' already exists on this schema!" % dimension.name)
        self.dimensions[dimension.name] = dimension

class PointCloud:
    def __init__(self, cloud_table, cloud_id, connection=''):
        self.cloud_id = cloud_id
        self.cloud_table = cloud_table
        
        if not connection:
            self.connect_string = "dbname=lidar host=192.168.1.113 user=hansent password=hansent"
        self.connection = psycopg2.connect(self.connect_string)
        
        self.block_table = self.get_block_table()
        self.schema = self.get_schema()
        
    def get_block_table(self):
        cur = self.connection.cursor()
        block_table = 'SELECT BLOCK_TABLE FROM %s where cloud_id = %d' % (self.cloud_table, self.cloud_id)
        block_table = cur.execute(block_table)
        block_table = cur.fetchone()[0]
        return block_table

    def get_bounds(self):
        cur = self.connection.cursor()
        bounds = 'select box3d(st_union(extent)) from %s' % self.block_table        
        cur.execute(bounds)
        
        bounds = cur.fetchone()[0]
        bounds = bounds.replace('BOX3D(','')
        bounds = bounds.replace(')', '')

        bounds = bounds.split(',')
        minx, miny, minz = bounds[0].split()
        maxx, maxy, maxz = bounds[1].split()
        # print minx, miny, minz, maxx, maxy, maxz
        return minx, miny, minz, maxx, maxy, maxz
    
    bounds = property(get_bounds)

# 
# from shapely.wkt import loads
# poly = loads(bounds)
# print poly


    def get_schema(self):
        
        cur = self.connection.cursor()
        xml = 'SELECT SCHEMA from %s where cloud_id=%d' % (self.cloud_table, self.cloud_id)
        cur.execute(xml)
        xml = cur.fetchone()[0]
        # f = open('schema.xml', 'wb')
        # f.write(xml)
        # f.close()

        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        schema = Schema()
        i = 0
        for child in root.getchildren():
            dim = Dimension(child)
            dim.index = i
            schema.append(dim)
            i = i + 1
        
        return schema;
    
    def get_numpy_frmt(self):
        types = {   'int8_t'   : np.int8,
                    'uint8_t'  : np.uint8,
                    'int16_t'  : np.int16,
                    'uint16_t' : np.uint16,
                    'int32_t'  : np.int32,
                    'uint32_t' : np.uint32,
                    'int64_t'  : np.int64,
                    'uint64_t' : np.uint64,
                    'float'    : np.float32, 
                    'double'   : np.float64}
        format = []
        for dimension in self.schema:
            ntype = types[dimension.interpretation]
            format.append((dimension.name, ntype))
        return format
        
    def get_blocks(self):

        cursor = self.connection.cursor()
        query = 'SELECT NUM_POINTS, POINTS from %s where cloud_id = %d ' % (self.block_table, self.cloud_id)
        cursor.execute(query)
        
        format = self.get_numpy_frmt()
        for row in cursor:
            yield row
            # count = int(row[0])
            # blob = row[1]
            # data = np.frombuffer(blob, dtype=format)
            # 
            # # probably some smart numpy way to get this 
            # # slice without a copy and coersion into a list - hobu
            # x = np.array([i[0] for i in data])
            # y = np.array([i[1] for i in data])
            # z = np.array([i[2] for i in data])
            # 
            # yield (x, y, z)
    blocks = property(get_blocks)
    
    def get_dimension(self, dimension, block):
        count = int(row[0])
        blob = row[1]
        data = np.frombuffer(blob, dtype=format)
        yield np.array([i[dimension.index] for i in block])

if __name__ == '__main__':
    
    cloud_table = 'sthelens_cloud'
    cloud_id = 1
    p = PointCloud(cloud_table, cloud_id)
        
    bounds = p.bounds
    byte_size = sum([int(i.size) for i in p.schema])
    
    
    
    
    for block in p.blocks:
        x = p.get_dimension(p.schema['X'], block)
        y = p.get_dimension(p.schema['Y'], block)
        z = p.get_dimension(p.schema['Z'], block)
