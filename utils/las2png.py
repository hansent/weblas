import struct
import numpy as np
import PIL.Image as Image
import laspy.file as las_file
from scipy.spatial import cKDTree
DIM = 2048

img_l = Image.new("L", (DIM, DIM))
img_rgba = Image.new("RGB", (DIM, DIM))
f = las_file.File("../app/data/mount_st_helens.las")















"""
vmax = f.header.max
vmin = f.header.min
print "raw max", vmax
print "raw min", vmin

norm_max = [vmax[i] - f.header.min[i] for i in range(3)]
print "normalized max:", norm_max
print #"x/y aspect:", norm_max[0]/norm_max[1]v
print "normalizing coordinates..."
vx = (f.x.astype(np.float32) - vmin[0] )/ norm_max[0] * DIM
vy = (f.y.astype(np.float32) - vmin[1] )/ norm_max[1] * DIM
vz = (f.z.astype(np.float32) - vmin[2] )/ norm_max[2]
#points = np.vstack((vx, vy, vz)).transpose()

print "creating heightmap from", len(vx), "points"
pix_buffer_l = img_l.load()

for i in range(len(vx)):
    x,y = map(int, (vx[i], vy[i]))
    pix_buffer_l[x,y] = int(vz[i] * 254)

for p in points:
    x = int(p[0])
    y = int(p[1])
    if pix_buffer[x,y] != (0,0,0,0):
        continue

    z = int(p[2] * (2**32 -1))
    rgba = struct.unpack("BBBB", struct.pack(">I", z))
    pix_buffer[x,y] = rgba
"""

img_l.save("height3.png")
