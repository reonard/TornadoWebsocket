__author__ = 'reonard'

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.gen
import time
import json
import tornado.httpclient

tornado.httpclient.AsyncHTTPClient.fetch()


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
        decoded = json.load(message)
        self.process_message(decoded)
        print message

    def on_close(self):
        if self.tid in connectedClient.keys():
            del connectedClient[self.tid]
            print "close"

    def __process_message(self, json_message):
        action_type = json_message.get('type')
        result = json_message.get('result')
        if action_type == 'HB':
            self.tid = result
            if self.tid not in connectedClient.keys():
                connectedClient[self.tid] = self
            print ("%s is beating" % self.tid)
            self.__heartbeatRslt(result)

        elif action_type == 'InqResp':
            self.__inquiryRslt(result)

        elif action_type == 'UpdResp':
            self.__updateRslt(result)

    def __heartbeatRslt(self, result_msg):
        print result_msg
        resp = json.dumps({'type': 'HB', 'command': 'Received'})
        self.write_message(resp, 0)

    def __inquiryRslt(self, result_msg):
        print result_msg

    def __updateRslt(self, result_msg):
        print result_msg


class ManagerHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        command = self.get_argument('command', ' ')
        target = self.get_argument('target', ' ')
        print target
        self.write("%s Client is Live </br>" % len(connectedClient))
        self.write("Process command is %s, target is %s" % (command, target))

        if target in connectedClient.keys():
            print "target found, sending"
            json_cmd = json.dumps({'type': 'INQ', 'command': command})
            connectedClient[target].write_message(json_cmd)

        yield tornado.gen.Task(self.wait, {})

    def wait(self, args, callback):
        time.sleep(5)
        return


if __name__ == "__main__":
    app = Application()
    app.listen(8081)
    tornado.ioloop.IOLoop.instance().start()