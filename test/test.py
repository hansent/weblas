import unittest

from plasio import lasfile

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


def test_plas():
    las = unittest.TestLoader().loadTestsFromTestCase(LasTestCase)


    return unittest.TestSuite([las])