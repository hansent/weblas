import png
import psycopg2
import numpy as np
import bounds
from PIL import Image

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


#only works for getters!
class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()



class PGPointCloud(pointcloud.PointCloud):

    def __init__(self, connection, cloud_table, cloud_id, *args, **kwargs):
        self.cloud_id = cloud_id
        self.cloud_table = cloud_table
        self.connection = connection

        self.block_table = self.get_block_table()
        pointcloud.PointCloud.__init__(self, *args, **kwargs)
        self.rowcount = 20
        self.spatial_filter = None

    def get_block_table(self):
        cur = self.connection.cursor()
        block_table = 'SELECT BLOCK_TABLE FROM %s where cloud_id = %d' % (self.cloud_table, self.cloud_id)
        block_table = cur.execute(block_table)
        block_table = cur.fetchone()[0]
        return block_table

    def get_bounds(self):
        cur = self.connection.cursor()
        #all of iowa
        b = 'select box3d(st_extent(extent)) from %s where cloud_id =  %s' % (self.cloud_table, self.cloud_id)
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


    def get_block_generator(self):
        def _gen():
            cursor = self.connection.cursor()
            query = 'SELECT NUM_POINTS, POINTS from %s where cloud_id = %d' % (self.block_table, self.cloud_id)
            cursor.execute(query)
            rows = cursor.fetchmany(self.rowcount)
            while rows:
                for row in rows:
                    yield np.frombuffer(row[1], dtype=self.schema.np_fmt)
                rows = cursor.fetchmany(self.rowcount)
        return _gen


    def splat_cloud(self, img_size=(1024, 1024)):
        #create image for heightmap
        print 'allocating %dx%d image buffer...' % img_size
        img = Image.new('L', img_size, 0)
        img_buff = img.load()

        bounds = self.bounds
        min_x, min_y, min_z = bounds.min
        max_x, max_y, max_z = bounds.max
        ext_x, ext_y, ext_z = bounds.max - bounds.min

        print min_x, min_y, min_z
        print max_x, max_y, max_z
        print ext_x, ext_y, ext_z

        import pprint
        pprint.pprint( self.schema.dimensions)

        blocks = self.get_block_generator()
        x_ind = self.schema['X'].index
        y_ind = self.schema['Y'].index
        z_ind = self.schema['Z'].index

        x_off = float(self.schema['X'].__dict__.get('offset', 0))
        y_off = float(self.schema['Y'].__dict__.get('offset', 0))
        z_off = float(self.schema['Z'].__dict__.get('offset', 0))

        sx = float(self.schema['X'].scale)
        sy = float(self.schema['Y'].scale)
        sz = float(self.schema['Z'].scale)


        print "ox,oy,oz", x_off, y_off, z_off
        print "sx,sy,sz", sx, sy, sz

        max_z = 0
        min_z = 99999999999999
        bl = 0

        buff = np.zeros(img_size)
        buff_int16 = np.zeros(img_size, dtype=np.uint16)


        #x =(point[x_ind] * sx + x_off - min_x) * img_size[0] / ext_x
        # = (point[y_ind] * sy + y_off - min_y) * img_size[1] / ext_y
        _img_scale_x = (img_size[0]-1) / ext_x
        _x_off =  (x_off * _img_scale_x) - (min_x * _img_scale_x)
        _sx = sx * _img_scale_x

        _img_scale_y = (img_size[1]-1) / ext_y
        _y_off =  (y_off * _img_scale_y) - (min_y * _img_scale_y)
        _sy = sy * _img_scale_y

        for block in blocks():
            bl += 1
            print "block", bl
            for point in block:
                x = int(point[x_ind] * _sy + _x_off)
                y = int(point[y_ind] * _sy + _y_off)
                z = point[z_ind]
                #if point[z_ind] > 18250:
                #    continue
                buff[x,y] = max(z, buff[x,y])
                min_z = min(min_z, z)
                max_z = max(max_z, z)
                #print x,y,z
            #print "z range: ", min_z, max_z


        max_val = (2**16 -1)
        z_range = max_z - min_z
        print min_z, max_z, z_range


        bins = [min_z + i for i in range(int(z_range))]
        hist, edges = np.histogram(buff, bins)

        for x in range(img_size[0]):
            for y in range(img_size[1]):
                buff_int16[x,y] = int( ((buff[x,y] - min_z) / z_range) * max_val )


        pngfile = open('../lodcache/cloud_%s.png' % self.cloud_id, 'wb')
        png_writer = png.Writer(img_size[0], img_size[1],
                           greyscale=True,
                           alpha=False,
                           bitdepth=16)

        png_writer.write(pngfile, buff_int16)
        pngfile.close()
        return hist, edges

import sys
postgis_connection = psycopg2.connect("dbname=iowa user=plasio")
cloud_table = 'iowa_cloud'
cloud_id = int(sys.argv[1])
print "CLOUD TABLE:", cloud_table
print "CLOUD ID:", cloud_id
#print [cid for cid in all_cloud_ids()]
p = PGPointCloud(postgis_connection, cloud_table, cloud_id)
hist, edges = p.splat_cloud()
