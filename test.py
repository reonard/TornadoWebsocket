import websocket
import thread
import time
import re
import MySQLdb

COnn = 0

def heartbeatRes():
    pass

def inquiryRes(ws, inq):
    #cursor = db.cursor
    ws.send(result)

def on_message(ws, message):
    print message
    rsl = re.search(r'(.*)-:-(.*)', message)
    if rsl:
        rsl.group(1)

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
            ws.send("HB2")
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