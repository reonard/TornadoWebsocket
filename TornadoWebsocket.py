__author__ = 'reonard'

import tornado.escape
from tornado import ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.gen
import time
import json
import tornado.httpclient
from tornado.concurrent import Future

MAX_REQUEST = 50

connectedClient = {}


def parse_json_resp(json_message):
    action_type = json_message.get('type')
    result = json_message.get('result')
    resp_id = json_message.get('respID')
    return action_type, result, resp_id


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [(r"/monitor", MonitorHandler),
                    (r"/manager", ManagerHandler),]
        tornado.web.Application.__init__(self, handlers)


class MonitorHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.tid = -1
        self.wait_for_resp = {}
        self.nextID = 1

    def open(self):
        print "connected"

    def on_message(self, message):
        decoded = json.loads(message)
        self.__process_message(decoded)
        print message

    def on_close(self):
        if self.tid in connectedClient.keys():
            del connectedClient[self.tid]
            print "close"

    def __process_message(self, json_message):

        action_type, result, resp_id = parse_json_resp(json_message)

        if action_type == 'HB':
            self.tid = result
            if self.tid not in connectedClient.keys():
                connectedClient[self.tid] = self
            print ("%s is beating" % self.tid)
            self.__heartbeatRslt(result)

        elif action_type == 'InqResp':
            print resp_id, self.wait_for_resp.keys()
            if int(resp_id) in self.wait_for_resp.keys():
                print "informing ManagePage"
                # Async call, return result message to webPage
                self.wait_for_resp[int(resp_id)].set_result(self.__inquiryRslt(result))
                del(self.wait_for_resp[int(resp_id)])
            print "after set result"

        elif action_type == 'UpdResp':
            self.__updateRslt(result)

    def __heartbeatRslt(self, result_msg):
        print result_msg
        resp = json.dumps({'type': 'HB', 'command': 'Received'})
        self.write_message(resp, 0)

    def __inquiryRslt(self, result_msg):
        print result_msg
        return result_msg

    def __updateRslt(self, result_msg):
        print result_msg


class ManagerHandler(tornado.web.RequestHandler):

    def get(self):
        target = self.get_argument('target', '')
        print target, connectedClient.get(target)
        self.render("./template/index.html", target=target, live=connectedClient.get(target))

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        command = self.get_argument('command', ' ')
        target = self.get_argument('target', ' ')
        if command and target:
            print target
            self.write("%s Client is Live </br>" % len(connectedClient))
            self.write("Process command is %s, target is %s </br>" % (command, target))
            print connectedClient.keys()
            if target in connectedClient.keys():
                future = Future()
                print "target found, sending"
                target_terminal = connectedClient[target]
                print connectedClient
                req_id = self.__get_terminal_req_id(target_terminal)
                # Handle multiple requests to the same terminal via adding request ID
                target_terminal.wait_for_resp[req_id] = future
                json_cmd = json.dumps({'type': 'INQ', 'command': command, 'reqID': req_id})
                target_terminal.write_message(json_cmd)
                # Suspend the request and wait for terminal return in $timeout
                result = yield tornado.gen.with_timeout(time.time() + 20, future)
            print "write page"
            self.write("result is %s" % result)
            self.finish()
        else:
            self.render()

    def __get_terminal_req_id(self, terminal):
        print terminal.nextID
        while terminal.nextID in terminal.wait_for_resp.keys():
            terminal.nextID += 1
            if terminal.nextID > MAX_REQUEST:
                terminal.nextID = 1
        return terminal.nextID


if __name__ == "__main__":
    app = Application()
    app.listen(8082)
    tornado.ioloop.IOLoop.instance().start()