import websocket
import thread
import time
import re
import json
import MySQLdb

COnn = 0


def heartbeatRes(wst, msg):
    print "HeartBeating"
    print msg


def inquiryRes(wst, msg):
    print "Inquiring"
    print msg
    jsonResp = json.dumps({'type': 'InqResp', 'result': 'Received %s' % msg})
    wst.send(jsonResp)


def updateRes(wst, msg):
    print "Updating"
    print msg

actionList = {'HB': heartbeatRes,
              'INQ': inquiryRes,
              'UPD': updateRes}


def process_message(wst, json_message):
    action_type = json_message.get('type')
    if action_type in actionList.keys():
        actionList.get(action_type)(ws, json_message.get('command'))


def on_message(ws, message):
    print message
    decoded = json.loads(message)
    process_message(ws, decoded)


def on_error(ws, error):
    print error


def on_close(ws):
    global COnn
    print "### closed ###"
    COnn = 0


def on_open(ws):
    print "open"
    global COnn
    COnn = 1

    def run(*args):
        while True:
            time.sleep(5)
            print "sending"
            ws.send("HB1")
        print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    # dbConn = MySQLdb.connect('localhost', 'root', 'root')

    while True:
        if not COnn:
            ws = websocket.WebSocketApp("ws://localhost:8081/monitor",
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.on_open = on_open
            ws.run_forever()

        time.sleep(10)