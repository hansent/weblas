import sys

def scale(v, s, o):
    
    return (v*s) + o

def descale(value, scale, offset):
    return (value - offset) / scale
    
from lasfile import LASFile
import laspy.file

f1 = laspy.file.File(sys.argv[1])
f2 = laspy.file.File(sys.argv[2])

def find_equal(p, points):
    p.make_nice()
    x2 = points.X
    xa = points.x
    y2 = points.Y
    ya = points.y
    z2 = points.Z
    za = points.z
    for i in range(len(x2)):
        
        x = scale(p.X, f1.header.scale[0], f1.header.offset[0])
        y = scale(p.Y, f1.header.scale[1], f1.header.offset[1])
        z = scale(p.Z, f1.header.scale[2], f1.header.offset[2])
        
        xp = x2[i]; yp = y2[i]; zp = z2[i]
        
        # print 'orig: ', x, y, z
        # print 'test: ', xp, yp, zp
        print 'candid: ', xa[i], ya[i], za[i]
        print 'source: ', x, y, z
        
        print 'candid: ', x2[i], y2[i], z2[i]
        print 'source: ', p.X, p.Y, p.Z

        print 'source z:', descale(z, f2.header.scale[2], f2.header.offset[2])
        print 'candidate z:', descale(za[i], f2.header.scale[2], f2.header.offset[2])

        if p.X == xp and p.Y == yp and p.Z == zp:
            print 'Found match '
            return True
    print 'Did not find match'
    return False
    


for p in f1:
    find_equal(p, f2)

for i in range(3):
    print 'source: %.12f %.12f' % (f1.header.scale[i], f1.header.offset[i])
    print 'candid: %.12f %.12f' % (f2.header.scale[i], f2.header.offset[i])
# for i in range(len(f1)):
    