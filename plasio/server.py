import sys
import logging
import os.path
import numpy as np
import json
import lasfile
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
            self.init_stream('../static/{0}'.format(msg_data['filename']))
            self.send_header()
            self.send_chunk()
        if msg_type == 'next_chunk':
            self.send_chunk()

    def init_stream(self, filename):
        self.point_cloud = lasfile.LASFile(filename)

    def send_header(self):
        data = {
            'num_points': self.point_cloud.num_points,
            'chunk_size': self.point_cloud.chunk_size,
            'scale_factor': self.point_cloud.scale_factor,
            'center': self.point_cloud.center,
            'extent': self.point_cloud.extents
        }
        self.send_msg('header', data)

    def send_msg(self, msg_type, data):
        self.write_message({'type': msg_type, 'data': data})

    def send_chunk(self):
        try:
            chunk = self.point_cloud.next()
            self.write_message(bytes(chunk), True)
        except StopIteration:
            return



class StaticFileHandler(tornado.web.StaticFileHandler):
    def get(self, path, include_body=True):
        if not path:
            path = 'index.html'
        return super(StaticFileHandler, self).get(path, include_body)

    def set_extra_headers(self, path):
        if self.settings.get('debug'):
            self.set_header('Cache-control', 'no-cache')


routes = [
    (r'/socket', SocketConnection),
    (r'/(.*)$', StaticFileHandler, {'path': './app'}),
]


if __name__ == '__main__':
    tornado.options.parse_command_line()
    tornado.autoreload.start()
    tornado.web.Application(routes, debug=True).listen(8080)
    tornado.ioloop.IOLoop.instance().start()


