from datetime import datetime
import glob
import http.server
import json
import os
import socketserver
import threading
import time
import subprocess
from urllib.parse import urlparse
from urllib.parse import parse_qs

from game_manager import GameManager

def simple_tail(fname, loop_at_end=False, sleep_interval=1, stop_flag=b'\034\n'):
    with open(fname, 'rb') as fin:
        line = fin.readline()
        while line:
            at_end = False
            where = fin.tell()
            next_line = fin.readline()
            if not next_line:
                at_end = True
            fin.seek(where)
            yield (line, at_end)
            line = fin.readline()

        while True:
            where = fin.tell()
            line = fin.readline()
            if not line:
                if loop_at_end:
                    time.sleep(sleep_interval)
                    fin.seek(where)
                else:
                    break
            else:
                if line == stop_flag:
                    break
                yield (line, True)

game_manager = GameManager()

PORT = 3000
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
                # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()
        
        html = f"<html><head></head><body><text style='white-space: pre; font-family: \"Lucida Console\", \"Courier New\", monospace;'>{game_manager.text_summary()}</text></body></html>"

        # Writing the HTML contents with UTF-8
        self.wfile.write(bytes(html, "utf8"))

        return

# Create an object of the above class
handler_object = MyHttpRequestHandler

def server_function(name):
    my_server = socketserver.TCPServer(("", PORT), handler_object)
    my_server.serve_forever()

def create_web_server():
    x = threading.Thread(target=server_function, args=(1,), daemon=True)
    x.start()


username = subprocess.check_output("echo %username%", shell=True).rstrip().decode("utf-8")
logs = glob.glob(f"C:\\Users\\{username}\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.*.log")
logs.sort()
last_log = logs.pop()

clear = lambda: os.system('cls')
create_web_server()

# Handle all other logs to catch up the game state
for log in logs:
    for (line, _) in simple_tail(log, False):
        event = json.loads(line.decode('UTF-8').rstrip())
        if game_manager.can_handle_event(event["event"]):
            game_manager.handle_event(event)
        elif not game_manager.can_ignore_event(event["event"]):
            print("Unknown event, please add to HANDLED_EVENTS or IGNORED_EVENTS lists")
            print(event)

# Handle last log and loop
# TODO: Handle a game restart without restarting the script
did_first_clear = False
for (line, at_end) in simple_tail(last_log, True):
    game_updated = False
    event = json.loads(line.decode('UTF-8').rstrip())
    if game_manager.can_handle_event(event["event"]):
        game_manager.handle_event(event)
        game_updated = True
    elif not game_manager.can_ignore_event(event["event"]):
        print("Unknown event, please add to HANDLED_EVENTS or IGNORED_EVENTS lists")
        print(event)
    if (game_updated and at_end) or (at_end and not did_first_clear):
        did_first_clear = True
        clear()
        print(game_manager.text_summary())
        # time.sleep(0.15)