import os.path
import tornado
import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.autoreload
import laspy.file
import numpy as np

f = laspy.file.File("static/data/serpent.las")
points = np.vstack((f.x, f.y, f.z)).transpose().ravel()
buffer_size = len(np.getbuffer(points))
print "points", len(points)/3, len(points)
print "buffersize", buffer_size, buffer_size/(8*3), buffer_size/8


class SocketConnection(tornado.websocket.WebSocketHandler):
    def open(self):
        self.offset = 0
        self.point_size = 3 * 8 # 3 (x,y,z) * int32 (8  bytes)
        self.chunk_size = self.point_size * 1024

    def send_chunk(self):
        chunk = np.getbuffer(points, self.offset, self.chunk_size)
        if len(chunk) == 0:
            return
        self.write_message(bytes(chunk), True)
        self.offset += self.chunk_size
        io_loop = tornado.ioloop.IOLoop.instance()
        io_loop.add_callback(self.send_chunk)

    def on_message(self, msg):
        self.send_chunk()

    def on_close(self):
        pass


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


