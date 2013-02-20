import unittest
import plas

from plas import lasfile

class LasTestCase(unittest.TestCase):
    serpent = './static/serpent-small.las'
    def setUp(self):
        pass

    def test_bounds(self):
        """Test LASfile bounds"""
        p = lasfile.LASFile(self.serpent)
        
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

        p = lasfile.LASFile(self.serpent)
        byte_size = sum([int(i.size) for i in p.schema])
        self.assertEqual(byte_size, 34)
        
        self.assertEqual(len(p), 20000)
        self.assertEqual(p.scales[0], 0.01)

    def tearDown(self):
        pass


def test_plas():
    las = unittest.TestLoader().loadTestsFromTestCase(LasTestCase)


    return unittest.TestSuite([las])