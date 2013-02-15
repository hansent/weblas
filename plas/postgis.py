import psycopg2
import numpy as np

import schema
import pointcloud
import bounds

class Dimension(schema.Dimension):
    def __init__(self, element, *args, **kwargs):
        # element.tag is something like 
        # '{http://pointcloud.org/schemas/PC/1.1}dimension'
        # extract the name space so we 
        ns = element.tag.replace('dimension', '')
        for attribute in element:
            self.__dict__[attribute.tag.replace(ns,'')] = attribute.text
        
        schema.Dimension.__init__(self, *args, **kwargs)

class PostGIS(pointcloud.PointCloud):
    def __init__(self, cloud_table, cloud_id, connection='', *args, **kwargs):
        self.cloud_id = cloud_id
        self.cloud_table = cloud_table
        
        if not connection:
            self.connect_string = "dbname=lidar host=192.168.1.113 user=hansent password=hansent"
        self.connection = psycopg2.connect(self.connect_string)
        
        self.block_table = self.get_block_table()
        pointcloud.PointCloud.__init__(self, *args, **kwargs)
        
    def get_block_table(self):
        cur = self.connection.cursor()
        block_table = 'SELECT BLOCK_TABLE FROM %s where cloud_id = %d' % (self.cloud_table, self.cloud_id)
        block_table = cur.execute(block_table)
        block_table = cur.fetchone()[0]
        return block_table

    def get_bounds(self):
        cur = self.connection.cursor()
        b = 'select box3d(st_union(extent)) from %s' % self.block_table        
        cur.execute(b)
        
        b = cur.fetchone()[0]
        b = b.replace('BOX3D(','')
        b = b.replace(')', '')

        b = b.split(',')
        minx, miny, minz = b[0].split()
        maxx, maxy, maxz = b[1].split()
        # print minx, miny, minz, maxx, maxy, maxz
        return bounds.Bounds(*tuple(float(x) for x in (minx, miny, minz, maxx, maxy, maxz)))
        # return minx, miny, minz, maxx, maxy, maxz

    def get_num_points(self):
        cur = self.connection.cursor()
        query = 'SELECT SUM(NUM_POINTS) from %s where cloud_id=%d' % (self.block_table, self.cloud_id)
        cur.execute(query)
        count = cur.fetchone()[0]
        return int(count)

    def get_schema(self):
        
        cur = self.connection.cursor()
        xml = 'SELECT SCHEMA from %s where cloud_id=%d' % (self.cloud_table, self.cloud_id)
        cur.execute(xml)
        xml = cur.fetchone()[0]


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

    

        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        s = schema.Schema()
        
        i = 0
        for child in root.getchildren():
            dim = Dimension(child)
            dim.index = i
            d = types[dim.interpretation]
            t = [(dim.name, d)]
            dim.np_fmt = np.dtype(t)
            s.append(dim)
            i = i + 1
        
        return s;


        
    def get_blocks(self):

        cursor = self.connection.cursor()
        query = 'SELECT NUM_POINTS, POINTS from %s where cloud_id = %d and block_id=1' % (self.block_table, self.cloud_id)
        cursor.execute(query)

        for row in cursor:
            yield row


            # x = np.array([i[0] for i in data])
            # y = np.array([i[1] for i in data])
            # z = np.array([i[2] for i in data])
            # 
            # yield (x, y, z)
    blocks = property(get_blocks)
    
    def get_dimension(self, dimension, block):
        count = int(block[0])
        blob = block[1]
        data = np.frombuffer(blob, dtype=self.schema.np_fmt)
        
        # # probably some smart numpy way to get this 
        # # slice without a copy and coersion into a list - hobu
        yield np.array([i[dimension.index] for i in data])

if __name__ == '__main__':
    
    cloud_table = 'sthelens_cloud'
    cloud_id = 1
    p = PostGIS(cloud_table, cloud_id)
        
    print p.bounds
    byte_size = sum([int(i.size) for i in p.schema])
    print byte_size
    print p.schema
    
    print len(p)
    
    
    print p.offsets, p.scales
    for block in p.blocks:
        x = p.get_dimension(p.schema['X'], block)
        y = p.get_dimension(p.schema['Y'], block)
        z = p.get_dimension(p.schema['Z'], block)
        
        l = list(x)
        print l
