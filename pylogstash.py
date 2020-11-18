import socket
import json
import sys
import os

import click

import collections

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        #print("k,v",k,v)
        new_key = str(parent_key) + sep + str(k) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        elif isinstance(v, collections.Iterable) and not isinstance(v,str):
            items.extend(flatten(dict(enumerate(v)), new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class LogStasher:
    def __init__(self, url=None, sep="."):
        if url is None:
            for n, m in {
                        'env': lambda: os.environ["LOGSTASH_ENTRYPOINT"].strip(),
                        'cdci-resources-file': lambda: open("/cdci-resources/logstash-entrypoint").read().strip(),
                    }.items(): 
                try:
                    self.url = m()
                    break
                except Exception as e:
                    print("failed to get logstash from",n , m)
        else:
            self.url = url

        self.sep = sep

        self.context = {}

    def set_context(self, c):
        self.context = c
    
    def log(self, msg):
        HOST, PORT = self.url.split(":")
        PORT = int(PORT)

        msg = flatten(dict(list(self.context.items()) + list(msg.items())), sep=self.sep)

        print("will stash:", json.dumps(msg))


        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            print("[ERROR] %s\n" % repr(e)) 
            

        try:
            sock.connect((HOST, PORT))
        except Exception as e:
            print("[ERROR] %s\n" % repr(e)) 

        sock.send(json.dumps(msg).encode())

        sock.close()


@click.command()
@click.argument("message")
def cli(message):
    LogStasher().log(json.loads(message))
