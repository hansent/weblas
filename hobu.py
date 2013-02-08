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

class PointCloud:
    def __init__(self, cloud_table, cloud_id, connection=''):
        self.cloud_id = cloud_id
        self.cloud_table = cloud_table
        
        if not connection:
            self.connect_string = "dbname=lidar host=192.168.1.61 user=hansent password=hansent"
        self.connection = psycopg2.connect(self.connect_string)
        
        self.block_table = self.get_block_table()
        
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

        f = open('schema.xml', 'wb')
        f.write(xml)
        f.close()


        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        dimensions = []
        for child in root.getchildren():
            dimensions.append(Dimension(child))
        
        return dimensions;
    schema = property(get_schema)
    
    def get_numpy_frmt(self, schema):
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
        for dimension in schema:
            ntype = types[dimension.interpretation]
            format.append((dimension.name, ntype))
        return format
        
    def get_blocks(self, format):
        cursor = self.connection.cursor()
        query = 'SELECT NUM_POINTS, POINTS from %s where cloud_id = %d ' % (self.block_table, self.cloud_id)
        cursor.execute(query)
        
        for row in cursor:
            count = int(row[0])
            blob = row[1]
            view = bytearray(blob)
            data = np.frombuffer(view, dtype=format)
            
            # probably some smart numpy way to get this 
            # slice without a copy and coersion into a list - hobu
            x = np.array([i[0] for i in data])
            y = np.array([i[1] for i in data])
            z = np.array([i[2] for i in data])
            
            yield (x, y, z)

if __name__ == '__main__':
    

    cloud_table = 'sthelens_cloud'
    cloud_id = 1
    p = PointCloud(cloud_table, cloud_id)

        
    bounds = p.bounds
    schema = p.schema
    byte_size = sum([int(i.size) for i in schema])
    frmt = p.get_numpy_frmt(schema)

    for block in p.get_blocks(frmt):
        print block[0].shape
