#!/usr/bin/env python3

import os
import random
import curses

from paho.mqtt import client as mqtt_client

broker = os.getenv('MQTT_DOMAIN')
port = os.getenv('MQTT_PORT')

client_id = f'python-mqtt-{random.randint(0, 1000)}'

mqtt_user = os.getenv('MQTT_USER')
mqtt_passwd = os.getenv('MQTT_PASSWD')

mqtt_connected = False
temperature = "no data"


def connect_mqtt() -> mqtt_client.Client:
    def on_connect(client, userdata, flags, rc):
        global mqtt_connected
        _ = client
        _ = userdata
        _ = flags
        if rc == 0:
            mqtt_connected = True
        else:
            raise Exception(f"Failed to connect, return code {rc}")
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(mqtt_user, mqtt_passwd)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client.Client):
    def on_message(client, userdata, msg):  #noqa
        client = client
        userdata = userdata
        global temperature
        if str(msg.topic) == 'myroom/temperature':
            temperature = msg.payload.decode()

    client.subscribe("myroom/temperature")
    client.on_message = on_message


def main(stdscr):
    global mqtt_connected
    global temperature

    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

    curses.noecho()
    curses.cbreak()
    stdscr.timeout(1000)

    while True:
        if not mqtt_connected:
            stdscr.addstr(0, 0, "Connection to mqtt broker...")
        else:
            stdscr.addstr(0, 0, "Connected to mqtt broker.")
            stdscr.addstr(1, 0, f"Temperature: {temperature} °C  ")

        stdscr.addstr(3, 0, "Press q to exit")

        stdscr.refresh()
        key = stdscr.getch()
        if key < 0:
            pass

        if key == ord('q'):
            break

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)
