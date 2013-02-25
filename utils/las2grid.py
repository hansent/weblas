
import numpy as np
from PIL import Image
from laspy.file import File
from scipy.spatial import cKDTree

print "reading source file"
f = File("../app/data/mount_st_helens.las")

print "normalizing coordinates"
sx = 1.0/(f.header.max[0] - f.header.min[0])
sy = 1.0/(f.header.max[1] - f.header.min[1])
sz = 1.0/(f.header.max[2] - f.header.min[2])
vx = (f.x.astype(np.float32) - f.header.min[0]) * sx
vy = (f.y.astype(np.float32) - f.header.min[1]) * sy
vz = (f.z.astype(np.float32) - f.header.min[2]) * sz

print "building KD Tree"
xy_positions = np.vstack((vx, vy)).transpose()
tree = cKDTree(xy_positions)

print "generating image grid"
img = Image.new("F", (256, 256))
buff = img.load()

print "sampling data..."
for x in range(256):
    print "row {0}/256".format(x)
    for y in range(256):
        fx, fy = x/256., y/256.
        idx = tree.query(np.array([fx,fy]))[1]
        buff[x,y] = vz[idx]


print "saving output image"
img.save("out.tif")

#grid_x, grid_y = np.mgrid[0:1:256j, 0:1:256j]

#gird_z = griddata((f.x, f.y), f.z, (grid_x, grid_y))

#print grid_z




