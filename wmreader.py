#!/usr/bin/env python3


"""WiiMotion+ wekinator adaptor

This program sends data from a WiiMote to an OSC sink (such as the Wekinator)
"""


import argparse
import time

import cwiid

from pythonosc import osc_message_builder
from pythonosc import udp_client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send wiimote data to an OSC \
            receiver")
    parser.add_argument("--ip", default="127.0.0.1",
            help="The destination IP of the OSC receiver")
    parser.add_argument("--port", type=int, default=6448,
            help="The destination port of the OSC receiver")
    parser.add_argument("--message", default="/wek/inputs",
            help="The message path to use for communication with the OSC \
                    receiver")
    parser.add_argument("--use-motionplus", type=bool, default=True,
            help="Use the WiiMotion+ adapter")
    parser.add_argument("--buttons", type=bool, default=False,
            help="Send the button status")
    parser.add_argument("--delay", type=float, default=0.1,
            help="The time (in seconds) between messages")

    args = parser.parse_args()

    print("Arguments: ", vars(args))

    client = udp_client.SimpleUDPClient(args.ip, args.port)

    wm = None
    while not wm:
        try:
            wm = cwiid.Wiimote()
        except RuntimeError:
            print("Cannot connect to WiiMote. Hold down 1+2 on the controller.")
            print("Trying again...")

    print("Wiimote successfully connected!");
    wm.led = 1

    client_rpt_mode = cwiid.RPT_ACC

    if args.buttons:
        client_rpt_mode = client_rpt_mode | cwiid.RPT_BTN
    
    if args.use_motionplus:
        client_rpt_mode = client_rpt_mode | cwiid.RPT_EXT | cwiid.RPT_MOTIONPLUS

    wm.rpt_mode = client_rpt_mode

    if args.use_motionplus:
        wm.enable(cwiid.FLAG_MOTIONPLUS)

    print("Initial state: ", wm.state)

    while True:
        acc = wm.state['acc']
        msg = (float(acc[0]),float(acc[1]),float(acc[2]))

        if args.buttons:
            msg = (float(wm.state['buttons']),)+msg

        if args.use_motionplus:
            try:
                ar = wm.state['motionplus']['angle_rate']
                lr = wm.state['motionplus']['low_speed']
                angles = (float(ar[0]), float(ar[1]), float(ar[2]))
                lspeed = (float(lr[0]), float(lr[1]), float(lr[2]))
                msg += angles + lspeed
            except KeyError:
                msg += (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        print("Sending: ", msg)
        client.send_message(args.message, msg)
        time.sleep(args.delay)

