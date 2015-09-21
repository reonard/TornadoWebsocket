import websocket
import thread
import time
import json
import MySQLdb

COnn = 0


# class inquiryHandler():
#
#     def __init__(self):
#         self.connectted = 0
#         self.mysqlcon = MySQLdb.connect()
#         self.result = 0
#
#     def __exceuteSQL(self, sqlcommand):
#
#         if self.mysqlcon:
#             cur = self.mysqlcon.cursor()
#             try:
#                 self.result = cur.execute(sqlcommand)
#             except:
#                 print "Error Execute"
#                 self.result = 0
#             finally:
#                 return self.result
#         else:
#             print "Reconnecting MySQL"
#             self.try_to_reconnect()
#
#
#     def result2json(self):
#
#
#
#
#
#     def __opendb_connection(self):
#         database_con = MySQLdb.connect()
#
#     def try_to_reconnect(self):
#         self.__opendb_connection()


def heartbeatRes(wst, msg, respID):
    print "HeartBeating"
    print msg


def inquiryRes(wst, msg, respID):
    print "Inquiring"
    # time.sleep(9)
    print msg
    jsonResp = json.dumps({'type': 'InqResp', 'result': 'Received %s' % msg, 'respID': '%d' % respID })
    wst.send(jsonResp)


def updateRes(wst, msg, respID):
    print "Updating"
    print msg

actionList = {'HB': heartbeatRes,
              'INQ': inquiryRes,
              'UPD': updateRes}


def process_message(wst, json_message):
    action_type = json_message.get('type')
    respID = 0
    if action_type in actionList.keys():
        respID = json_message.get('reqID')
        actionList.get(action_type)(ws, json_message.get('command'), respID)


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
            print "sending"
            terminal_no = '2'
            ws.send(json.dumps({'type': 'HB', 'result': terminal_no}))
            time.sleep(300)
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