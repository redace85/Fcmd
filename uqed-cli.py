#!/usr/bin/env python3.7
# coding=utf-8
import os
import sys
import socket
import daemon
import logging

import config


ipc_path = './qed.ipc'
if not os.path.exists(ipc_path):
    print('start quant engine in daemon')
    context = daemon.DaemonContext(working_directory='./')

    from qev1 import QuantEngine
    with context:
        stream = open('qev1.log',mode='w')
        logging.basicConfig(stream = stream,
                            format='%(levelname)s:%(message)s',
                            level=config.logginglevel)

        import strategy_pos

        strategy_obj = strategy_pos.Position_Strategy()
        strategy_obj.init_strategy_data()

        qe = QuantEngine(strategy_obj)
        qe.run(ipc_path)
else:
    print('stop quant engine!')

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(ipc_path)
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    # send ipc cmd
    message = b'stop'
    sock.sendall(message)
    sock.close()