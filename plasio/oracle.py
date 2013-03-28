import numpy as np

import schema
import pointcloud
import bounds
import cx_Oracle 

class Dimension(schema.Dimension):
    def __init__(self, element, *args, **kwargs):
        # element.tag is something like
        # '{http://pointcloud.org/schemas/PC/1.1}dimension'
        # extract the name space so we
        ns = element.tag.replace('dimension', '')
        for attribute in element:
            self.__dict__[attribute.tag.replace(ns,'')] = attribute.text

        schema.Dimension.__init__(self, *args, **kwargs)

class Oracle(pointcloud.PointCloud):
    def __init__(self, connection, cloud_table, cloud_id, *args, **kwargs):
        self.cloud_id = cloud_id
        self.cloud_table = cloud_table
        self.connection = cx_Oracle.connect(connection)

        self.block_table = self.get_block_table()
        pointcloud.PointCloud.__init__(self, *args, **kwargs)
        self.rowcount = 20
        self.spatial_filter = None

    def get_block_table(self):
        cur = self.connection.cursor()
        block_table = 'SELECT A.CLOUD.BLK_TABLE FROM %s A where ID = %d' % (self.cloud_table, self.cloud_id)
        # clob = cur.var(cx_Oracle.CLOB)
        pc = cur.execute(block_table)
        pc = cur.fetchone()[0]
        return pc

    def get_bounds(self):
        return None
        # cur = self.connection.cursor()
        # b = 'select box3d(st_union(extent)) from %s' % self.block_table
        # cur.execute(b)
        # 
        # b = cur.fetchone()[0]
        # b = b.replace('BOX3D(','')
        # b = b.replace(')', '')
        # 
        # b = b.split(',')
        # minx, miny, minz = b[0].split()
        # maxx, maxy, maxz = b[1].split()
        # # print minx, miny, minz, maxx, maxy, maxz
        # return bounds.Bounds(*tuple(float(x) for x in (minx, miny, minz, maxx, maxy, maxz)))
        # return minx, miny, minz, maxx, maxy, maxz

    def get_num_points(self):
        cur = self.connection.cursor()
        query = 'SELECT SUM(NUM_POINTS) from %s where obj_id=%d' % (self.block_table, self.cloud_id)
        cur.execute(query)
        count = cur.fetchone()[0]
        return int(count)

    def get_schema(self):

        cur = self.connection.cursor()
        block_table = 'SELECT xmltype.getclobval(A.CLOUD.PC_OTHER_ATTRS) FROM %s A where ID = %d' % (self.cloud_table, self.cloud_id)
        # clob = cur.var(cx_Oracle.CLOB)
        pc = cur.execute(block_table)
        pc = cur.fetchall()
        xml = pc[0][0].read()



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



    def __iter__(self):

        cursor = self.connection.cursor()
        query = 'SELECT NUM_POINTS, POINTS from %s where obj_id = %d ' % (self.block_table, self.cloud_id)
        cursor.execute(query)

        rows = cursor.fetchmany(self.rowcount)

        output = None
        x_ind = self.schema['X'].index
        y_ind = self.schema['Y'].index
        z_ind = self.schema['Z'].index
        while rows:
            
            for row in rows:
                
                blob = row[1]
                data = np.frombuffer(blob.read(), dtype=self.schema.np_fmt)
                vx = np.array([i[x_ind] for i in data])
                vy = np.array([i[y_ind] for i in data])
                vz = np.array([i[z_ind] for i in data])
                points = np.vstack((vx, vy, vz)).transpose()

                # pluck out unique x,y,z tuples
                # output = np.vstack([np.array(u) for u in set([tuple(p) for p in points])])
                yield points

            rows = cursor.fetchmany(self.rowcount)

def scale(v, s, o):
    
    return (v*s) + o

def find_equal(a, candidates):
    x = a[0]
    y = a[1]
    z = a[2]
    print 'sour: ', x, y, z
    
    for c in candidates:
        xp = c[0]
        yp = c[1]
        zp = c[2]
        print 'cand: ', xp, yp, zp
        if (xp == x and yp == y and zp == z):
            print 'Found match '
            return True
    print 'Did not find match'
    return False
if __name__ == '__main__':
    connection = "grid/grid@localhost/orcl"
    import sys
    
    cloud_table = sys.argv[1]
    cloud_id = 1
    p = Oracle(connection, cloud_table, cloud_id)
    
    # print p.bounds
    # byte_size = sum([int(i.size) for i in p.schema])
    # print byte_size
    # for dim in p.schema:
    #     print dim
    # 
    # print len(p)
    # 
    
    from lasfile import LASFile
    import laspy.file
    
    f = laspy.file.File('/Users/hobu/dev/git/pdal/test/data/oracle/loadtest/small.las')
    # print f.X
    # print p.offsets, p.scales
    output = None
    
    files = np.vstack((f.X, f.Y, f.Z)).transpose()
    # print 'len(f.X): ', len(f.X)
    block = list(p)[0]
    
    
    # print files
    # print block

    print 'source: %.8f %.8f' % (f.header.scale[0], f.header.offset[0])
    print 'oracle: %.8f %.8f' % (float(p.schema['X'].scale), float(p.schema['X'].offset))

    print 'source: %.8f %.8f' % (f.header.scale[1], f.header.offset[1])
    print 'oracle: %.8f %.8f' % (float(p.schema['Y'].scale), float(p.schema['Y'].offset))

    print 'source: %.8f %.8f' % (f.header.scale[2], f.header.offset[2])
    print 'oracle: %.8f %.8f' % (float(p.schema['Z'].scale), float(p.schema['Z'].offset) )
    
    # print f.header.offset[0], f.header.scale[0]
    # print p.schema['X'].offset, p.schema['X'].scale
    # print f.header.offset[1], f.header.scale[1]
    # print p.schema['Y'].offset, p.schema['Y'].scale
    # print f.header.offset[2], f.header.scale[2]
    # print p.schema['Z'].offset, p.schema['Z'].scale

    for i in range(len(files)):
        find_equal(files[i], block)
    
    # print block
    # for i in range(len(f)):
    #     print i
    # 
    #     xa = f.X[i]
    #     xb = block[i][0]
    #     print xa, xb

        # point = block[0]
        # x = point[0]
        # print x
        # print scale(x, p.scales[0], p.offsets[0])
        # y = point[1]
        # z = point[2]
        # print x, y, z
        # break
            # output = np.vstack((output, block))
    # 
    # print 'shape: ', output.shape

