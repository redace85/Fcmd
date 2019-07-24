#!/usr/bin/env python3.7
# coding=utf-8
import os
import sys
import socket
import daemon
import logging
import getopt

import config


try:
    opts, args = getopt.getopt(sys.argv[1:], "ds:", ["debug", "signal="])
except getopt.GetoptError:
    print('uqed-cli -d -s <signal_str>')
    sys.exit(2)

run_in_debug = False
signal_str = ''
for opt, arg in opts:
    if opt in ('-d', '--debug'):
        run_in_debug = True
    elif opt in ('-s', '--signal'):
        signal_str = arg


def run_quant_engine(ipc_path, use_stdout=False):
    from qev1 import QuantEngine
    if use_stdout:
        stream = sys.stdout
    else:
        stream = open('qev1.log', mode='w')
    logging.basicConfig(stream=stream,
                        format='%(levelname)s # %(processName)s : %(message)s',
                        level=config.logginglevel)

    import strategy_ma

    strategy_obj = strategy_ma.Ma_pos_Strategy()
    strategy_obj.init_strategy_data()

    qe = QuantEngine(strategy_obj, mock_execution=config.mock_execution)
    qe.run(ipc_path)


ipc_path = './qed.ipc'
if not os.path.exists(ipc_path):
    if run_in_debug:
        print('start quant engine in debug mode')
        run_quant_engine(None, True)
    else:
        print('start quant engine in daemon')
        context = daemon.DaemonContext(working_directory='./')
        with context:
            run_quant_engine(ipc_path)
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

    os.unlink(ipc_path)
