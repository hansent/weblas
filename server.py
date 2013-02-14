import sys
import logging
import os.path
import numpy as np
import json
import laspy.file

import tornado
import tornado.autoreload
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket


class SocketConnection(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_close(self):
        pass

    def on_message(self, msg):
        msg = json.loads(msg)

        msg_type = msg.get('type')
        msg_data = msg.get('data')
        if msg_type == 'load':
            self.init_stream('app/data/{}'.format(msg_data['filename']))
            self.send_header()
            self.send_chunk()
        if msg_type == 'next_chunk':
            self.send_chunk()

    def init_stream(self, filename):
        f = laspy.file.File(filename)
        self.minima = f.header.min
        self.maxima = f.header.max
        vx = f.x.astype(np.float32)
        vy = f.y.astype(np.float32)
        vz = f.z.astype(np.float32)
        points = np.vstack((vx, vy, vz)).transpose()[::9]
        points = points - self.minima
        size = [0.5*(self.maxima[i]-self.minima[i]) for i in range(3) ]
        points = (points - size) * -.01
        #points = points * (10./self.maxima[i]-self.minima[i])

        self.points = points.ravel().astype(np.float32)

        self.num_points = len(self.points)
        self.item_size = self.points.dtype.itemsize
        self.point_size = self.item_size * 3
        self.buffer_size = self.point_size * self.num_points
        self.chunk_size = self.point_size * 10000
        self.offset = 0

    def send_header(self):
        data = {
            'num_points': self.num_points,
            'item_size': self.item_size,
            'point_size': self.point_size,
            'buffer_size': self.buffer_size,
            'chunk_size': self.chunk_size,
            'minima': self.minima,
            'maxima': self.maxima
        }
        self.send_msg('header', data)

    def send_msg(self, msg_type, data):
        self.write_message({'type': msg_type, 'data': data})

    def send_chunk(self):
        chunk = np.getbuffer(self.points, self.offset, self.chunk_size)
        if len(chunk) == 0:
            return
        self.write_message(bytes(chunk), True)
        self.offset += self.chunk_size


class StaticFileHandler(tornado.web.StaticFileHandler):
    def get(self, path, include_body=True):
        if path is None:
            path = 'index.html'
        return super(StaticFileHandler, self).get(path, include_body)

    def set_extra_headers(self, path):
        if self.settings.get('debug'):
            self.set_header('Cache-control', 'no-cache')


routes = [
    (r'/socket', SocketConnection),
    (r'/(index\.html)?$', StaticFileHandler, {'path': './app'}),
    (r'/(.*)$', StaticFileHandler, {'path': './app'}),
]


if __name__ == '__main__':
    tornado.options.parse_command_line()
    tornado.autoreload.start()
    tornado.web.Application(routes, debug=True).listen(8080)
    tornado.ioloop.IOLoop.instance().start()


