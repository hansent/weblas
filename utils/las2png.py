import laspy.file as las_file
import PIL.Image as Image
import sys
import numpy as np
import struct



RESOLUTION = (512, 512)
DECIMATION_FACTOR = 10


#read las file
f = las_file.File("../static/st-helens.las")


#decimate
print "decimating by factor {0}".format(DECIMATION_FACTOR)
vx = f.x.astype(np.float32)[::DECIMATION_FACTOR]
vy = f.y.astype(np.float32)[::DECIMATION_FACTOR]
vz = f.z.astype(np.float32)[::DECIMATION_FACTOR]


#normalize each dimension
print "normalizing dimensions"
x_min, x_max = min(vx), max(vx)
y_min, y_max = min(vy), max(vy)
z_min, z_max = min(vz), max(vz)
vx = (vx - x_min) / (x_max - x_min)
vy = (vy - y_min) / (y_max - y_min)
vz = (vz - z_min) / (z_max - z_min)


#create image for heightmap
print "allocating image buffer"
img = Image.new("L", RESOLUTION, 0)
img_buff = img.load()

#splat heigth data
num_points = len(vx)
progress_steps = num_points/200
for i in range(num_points):
    x = int(vx[i] * (RESOLUTION[0]-1))
    y = int(vy[i] * (RESOLUTION[1]-1))
    z = int(vz[i] * 254)
    if img_buff[x,y] == 0:
        img_buff[x,y] = z

    if  i % progress_steps == 100:
        percentage = int( float(i*100)/num_points )
        sys.stdout.write( "\rsplatting height data: {0:d}% ".format(percentage+1))
        sys.stdout.flush()


img.save("heightmap.png")


'''
norm_max = [vmax[i] - f.header.min[i] for i in range(3)]
print "normalized max:", norm_max
print #"x/y aspect:", norm_max[0]/norm_max[1]v
print "normalizing coordinates..."
vx = (f.x.astype(np.float32)[::100] - vmin[0] )/ norm_max[0] * (DIM-1)
vy = (f.y.astype(np.float32)[::100] - vmin[1] )/ norm_max[1] * (DIM-1)
vz = (f.z.astype(np.float32) - vmin[2] )/ (vmax[2] * f.header.scale[2])
print "vz", min(vz), max(vz)
points = np.vstack((vx, vy, vz)).transpose()

print "creating heightmap from", len(vx), "points"
pix_buffer = img_rgba.load()
#for i in range(len(vx)/10):
#    x,y = map(int, (vx[i*10], vy[i*10]))
#    pix_buffer_l[x,y] = min( max(0,int(vz[i] * 254)), 1)



for p in points:
    x = int(p[0])
    y = int(p[1])

    z = p[2] * 100# int(p[2] * (2**32 -1))
    #rgba = struct.unpack("BBBB", struct.pack(">I", z))
    print x,y,z
    #pix_buffer[x,y] = rgba
    #print struct.pack("I", z)

img_l.save("height3.png")
'''
