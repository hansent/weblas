import os.path
import tornado
import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.autoreload
import laspy.file
import sys
import numpy as np


class SocketConnection(tornado.websocket.WebSocketHandler):
    def open(self):
        print "socket opened"
        pass

    def on_message(self, msg):
        print "message", msg
        if msg == "init":
            self.init_stream()
            self.send_header()
        self.send_chunk()

    def on_close(self):
        pass

    def init_stream(self, filename="static/data/serpent.las"):
        f = laspy.file.File(filename)
        self.minima = f.header.min
        self.maxima = f.header.max

        vx = f.x.astype(np.float32)
        vy = f.y.astype(np.float32)
        vz = f.z.astype(np.float32)
        points = np.vstack((vx, vy, vz)).transpose()[0::100]
        points = (points - self.minima) /10.0 #/ max(self.maxima)
        self.points = points.ravel().astype(np.float32)

        self.num_points = len(self.points)
        self.item_size = self.points.dtype.itemsize
        self.point_size = self.item_size * 3
        self.buffer_size = self.point_size * self.num_points
        self.chunk_size = self.point_size * 10000
        self.offset = 0

    def send_header(self):
        self.write_message({
            'num_points': self.num_points,
            'item_size': self.item_size,
            'point_size': self.point_size,
            'buffer_size': self.buffer_size,
            'chunk_size': self.chunk_size,
            'minima': self.minima,
            'maxima': self.maxima,
        })

    def send_chunk(self):
        chunk = np.getbuffer(self.points, self.offset, self.chunk_size)
        print self.points
        if len(chunk) == 0:
            return
        self.write_message(bytes(chunk), True)
        self.offset += self.chunk_size
        #io_loop = tornado.ioloop.IOLoop.instance()
        #io_loop.add_callback(self.send_chunk)









class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class DevStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")


routes = [
    (r"/static/(.*)", DevStaticFileHandler, {'path': './static'}),
    (r'/socket', SocketConnection),
    (r'/', IndexHandler),
]

settings = {
    'template_path': './template',
    'debug' : True
}

if __name__ == '__main__':
    app = tornado.web.Application(routes, **settings)
    app.listen(8080)
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(io_loop)
    io_loop.start()


