# -*- coding: UTF-8 -*-
import urlparse
import websocket
import thread
import time
import json
import MySQLdb
import wmi
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

COnn = 0
TESTDB = ("127.0.0.1", "root", "root", "sxtcimc")
TERNO = ""

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
    respmsg={}
    row_num = 0
    dbConn = MySQLdb.connect(*TESTDB, charset="gb2312")
    cursor = dbConn.cursor()
    result_num = cursor.execute(msg)
    rows = cursor.fetchall()
    desc = cursor.description
    print desc
    row_data = []
    data_respmsg = []
    for col in desc:
        row_data.append(col[0])
    respmsg["headcol"] = row_data

    for row in rows:
        row_num += 1
        colnum = 0
        row_data = []
        for col in desc:
            print col[0]
            row_data.append(str(row[colnum]).encode("utf-8"))
            print row_data
            colnum += 1
        data_respmsg.append(row_data)
        respmsg["data"] = data_respmsg

    print respmsg
    jsonResp = json.dumps({'type': 'InqResp', 'result': respmsg, 'respID': '%d' % respID})
    dbConn.close()
    wst.send(jsonResp)

def updateRes(wst, msg, respID):
    print "Updating"
    print msg


def killApp(wst, msg, respID):
    print msg
    proc = wmi.WMI()
    for process in proc.Win32_Process(name="SXT.CIMC.ParcelExtractSystem.exe"):
        result = process.Terminate()
    jsonResp = json.dumps({'type': 'KILLResp', 'result': "Killed", 'respID': '%d' % respID})
    wst.send(jsonResp)


actionList = {'HB': heartbeatRes,
              'INQ': inquiryRes,
              'UPD': updateRes,
              'KILL': killApp}


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
            terminal_no = TERNO
            ws.send(json.dumps({'type': 'HB', 'result': terminal_no}))
            time.sleep(600)
        print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    dbConn = MySQLdb.connect(*TESTDB,charset="gb2312")
    cursor = dbConn.cursor()
    cursor.execute("select terminalno from tblcimcsysver")
    TERNO = cursor.fetchone()[0]
    dbConn.close()
    print TERNO

    while True:
        if not COnn:
            print "Con"
            ws = websocket.WebSocketApp("ws://103.59.216.68:6789/monitor",
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            print "After"
            ws.on_open = on_open
            ws.run_forever()

        time.sleep(10)
