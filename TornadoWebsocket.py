__author__ = 'reonard'

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import time

connectedClient = {}

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [(r"/monitor", MonitorHandler),
                    (r"/manager/", ManagerHandler), ]
        tornado.web.Application.__init__(self, handlers)


class MonitorHandler(tornado.websocket.WebSocketHandler):

    tid = -1

    def open(self):
        print "connected"

    def on_message(self, message):
        time.sleep(1)
        self.tid = message[2:]
        if self.tid not in connectedClient.keys():
            connectedClient[self.tid] = self
        print ("%s is beating" % self.tid)
        self.write_message("Received", 0)
        print message

    def on_close(self):
        if self.tid in connectedClient.keys():
            del connectedClient[self.tid]
            print "close"


class ManagerHandler(tornado.web.RequestHandler):

    def get(self):
        command = self.get_argument('command', ' ')
        target = self.get_argument('target', ' ')
        print target
        self.write("%s Client is Live </br>" % len(connectedClient))
        self.write("Process command is %s, target is %s" % (command, target))

        if target in connectedClient.keys():
            print "target found, sending"
            connectedClient[target].write_message(command)


if __name__ == "__main__":
    app = Application()
    app.listen(8081)
    tornado.ioloop.IOLoop.instance().start()