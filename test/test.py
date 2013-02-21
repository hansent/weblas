import unittest

from plasio import lasfile

postgis_connection = "dbname=lidar host=localhost"

class LasTestCase(unittest.TestCase):
    serpent = './static/serpent-small.las'
    def setUp(self):
        self.file = lasfile.LASFile(self.serpent)

    def test_bounds(self):
        """Test LASfile bounds"""
        p = self.file
        
        minx = '%.4f' % p.bounds.minx
        miny = '%.4f' % p.bounds.miny
        minz = '%.4f' % p.bounds.minz
        maxx = '%.4f' % p.bounds.maxx
        maxy = '%.4f' % p.bounds.maxy
        maxz = '%.4f' % p.bounds.maxz

        self.assertEqual(minx, '289729.1000')
        self.assertEqual(miny, '4320942.6100')
        self.assertEqual(minz, '166.7800')

        self.assertEqual(maxx, '290047.2000')
        self.assertEqual(maxy, '4321105.9900')
        self.assertEqual(maxz, '184.8700')
    
    def test_header(self):
        """Test LASfile schema"""
        p = self.file
        byte_size = sum([int(i.size) for i in p.schema])
        self.assertEqual(byte_size, 34)
        
        self.assertEqual(len(p), 20000)
        self.assertEqual(p.scales[0], 0.01)
        self.assertEqual(p.points.dtype.itemsize, 4)

    def test_chunk_fetch(self):
        """Returning a chunk size returns correct values"""
        p = self.file
        count = 20000
        self.assertEqual(len(p), count)
        
        # chunk size is 10000
        chunk = p.next()
        
        self.assertEqual('%.2f'% chunk[0][0], '289814.16')
        self.assertEqual('%.2f'% chunk[0][1], '4320978.50')
        self.assertEqual('%.2f'% chunk[0][2], '170.76')
        
        self.assertEqual(len(chunk), p.chunk_size)
        
        chunk = p.next()
        self.assertRaises(StopIteration, p.next)

    def test_chunk_iteration(self):
        """Iterating a file returns chunks"""
        p = self.file
        
        count = 0
        for chunk in p:
            count = count + len(chunk)
        self.assertEqual(count, len(p))

    def test_chunk_scaling(self):
        """Scaling chunks works"""
        p = self.file

        # get first chunk
        chunk = p.next()
        scaled = p.scale(chunk)
        self.assertEqual('%.2f'% chunk[0][0], '289814.16')
        self.assertEqual('%.2f'% chunk[0][1], '4320978.50')
        self.assertEqual('%.2f'% chunk[0][2], '170.76')

        self.assertEqual('%.2f'% scaled[0][0], '2350.92')
        self.assertEqual('%.2f'% scaled[0][1], '991.98')
        self.assertEqual('%.2f'% scaled[0][2], '110.01')
       
        
    def tearDown(self):
        pass


class PostgisTestCase(unittest.TestCase):
    
    
    serpent = ''
    def setUp(self):
        from plasio import postgis
        self.p = postgis.PostGIS(postgis_connection, 'sthelens_cloud', 1)

    def test_length(self):
        """Test PostGIS count"""
        count = len(self.p)
        self.assertEqual(count, 12388139)

    def test_bounds(self):
        """Test PostGIS bounds"""
        b = self.p.bounds
        minx = '%.4f' % b.minx
        miny = '%.4f' % b.miny
        minz = '%.4f' % b.minz
        maxx = '%.4f' % b.maxx
        maxy = '%.4f' % b.maxy
        maxz = '%.4f' % b.maxz

        self.assertEqual(minx, '560022.4100')
        self.assertEqual(miny, '5114840.6000')
        self.assertEqual(minz, '1207.5700')

        self.assertEqual(maxx, '564678.4300')
        self.assertEqual(maxy, '5120950.9000')
        self.assertEqual(maxz, '2539.3800')
    
    def test_chunk_iteration(self):
        """Iterating a postgis table returns chunks"""
        query_count = 0
        block_count = 155
        for block in iter(self.p):
            query_count += 1
   
        self.assertEqual(query_count, block_count)

    # def test_chunk_scaling(self):
    #     """Scaling chunks works"""
    #     p = self.file
    # 
    #     # get first chunk
    #     chunk = p.next()
    #     scaled = p.scale(chunk)
    #     self.assertEqual('%.2f'% chunk[0][0], '289814.16')
    #     self.assertEqual('%.2f'% chunk[0][1], '4320978.50')
    #     self.assertEqual('%.2f'% chunk[0][2], '170.76')
    # 
    #     self.assertEqual('%.2f'% scaled[0][0], '2350.92')
    #     self.assertEqual('%.2f'% scaled[0][1], '991.98')
    #     self.assertEqual('%.2f'% scaled[0][2], '110.01')

    def tearDown(self):
        pass

def test_plas():
    las = unittest.TestLoader().loadTestsFromTestCase(LasTestCase)

    tests = [las]
    
    try:
        import psycopg2
        
        try:
            conn = psycopg2.connect(postgis_connection)
            postgis = unittest.TestLoader().loadTestsFromTestCase(PostgisTestCase)
            tests.append(postgis)
        except psycopg2.OperationalError:
            pass
    except ImportError:
        pass
    
    return unittest.TestSuite(tests)