import socket
import json
import sys
import os

import click

import collections

import logging

logger = logging.getLogger("pylogstash:" + __name__)

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
                    logger.info("set up logstash link from %s: %s", n, m)
                    break
                except Exception as e:
                    logger.debug("failed to get logstash from %s: %s", n, m)
        else:
            logger.info("set up logstash link from argument")
            self.url = url

        self.sep = sep

        self.context = {}

    def set_context(self, c):
        self.context = c
    
    def log(self, msg):
        if isinstance(msg, str):
            msg_bytes = msg.encode()
        elif isinstance(msg, dict):
            msg_bytes = json.dumps(flatten(dict(list(self.context.items()) + list(msg.items())), sep=self.sep)).encode()
        else:
            raise RuntimeError("unknown type message: %s", type(msg))

        if getattr(self, 'url', None) is None:
            logger.info("logstash fallback: %s", msg_bytes)
        else:
            HOST, PORT = self.url.split(":")
            PORT = int(PORT)

            logger.debug("send to logstash: %s", msg_bytes)


            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as e:
                logger.error("ERROR creating socket") 
                return
                

            try:
                sock.connect((HOST, PORT))
            except Exception as e:
                logger.error("ERROR connecting to host %s:%s %s\n", HOST, PORT, repr(e)) 
                return

            try:
                sock.send(msg_bytes)
            except Exception as e:
                logger.error()

            sock.close()


@click.command()
@click.argument("message")
def cli(message):
    LogStasher().log(json.loads(message))
