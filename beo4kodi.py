#! /bin/env python

# Python Arduino Bang & Olufsen Beo4 Remote using B&O IR Eye to control Kodi TV
#
# Todos:
#   1. Subscribe to notifications and keep state on current player and status
#   2. Periodically fetch status in case status changes
#
# Author: CP (c) 2018
# Github: unclaimedpants
#

from time import sleep
from nptime import nptime
from kodipydent import Kodi
from datetime import timedelta

import logging
import threading

USERNAME = ''
PASSWORD = ''
KODI_HOST = ''
IR_DEVICE = '/dev/ttyACM0'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def getContext(kodi):
    '''
    Returns the current Kodi context
    '''

    try:
        return kodi.GUI.GetProperties(['currentwindow'])['result']['currentwindow']['label']
    except:
        log.debug('No currentwindow result')
        return ''


def getPlayer(kodi):
    '''
    Returns with the current active player with the time and position

        {
          u'playerid': 0,
          u'type': u'audio',

          u'totaltime': {
            u'hours': 0,
            u'seconds': 4,
            u'minutes': 4,
            u'milliseconds': 871
          },

          u'time': {
            u'hours': 0,
            u'seconds': 59,
            u'minutes': 3,
            u'milliseconds': 65
          }
        }
    '''
    try:
        obj = {}
        player = kodi.Player.GetActivePlayers()['result'].pop()
        timer = kodi.Player.GetProperties(playerid=player['playerid'], properties=['time', 'totaltime'])['result']
        obj.update(player)
        obj.update(timer)
        return obj
    except:
        log.debug('No active player')
        return {}


def time_to_obj(time_str):
    '''
    Converts time to an object
    '''
    return {'hours':time_str.hour, 'minutes':time_str.minute, 'seconds':time_str.second}


def obj_to_time(obj):
    '''
    Converts a time object to time
    '''
    return nptime(obj['hours'], obj['minutes'], obj['seconds'])


def sub_time(obj, diff):
    '''
    Returns current play position - time {'hours':0, 'minutes':10, 'seconds':0}
    '''
    a = obj_to_time(obj['time']) - diff
    b = obj_to_time(obj['totaltime'])
    if a > b:
        return time_to_obj(nptime(0, 0, 0))
    return time_to_obj(a)


def add_time(obj, diff):
    '''
    Returns current play position + time {'hours':0, 'minutes':10, 'seconds':0}
    '''

    a = obj_to_time(obj['time']) + diff
    b = obj_to_time(obj['totaltime'])
    if a < b:
        return time_to_obj(a)
    return time_to_obj(b)


def ir_command(kodi, remote, command):
    '''
    Processes a received IR command
    '''

    # Power off
    if command == '00001C':
        playerObj = getPlayer(kodi)
        kodi.Player.PlayPause(playerObj.get('playerid'))
        remote['mode'] = None
        return

    if remote['mode'] != '00008B':
        if command == '00008B':
            remote['mode'] = '00008B'
            log.debug('Remote Activated: Beo remote in PC mode')
            kodi.Input.ShowOSD()
            return
        log.debug('Remote Inactive: Beo remote is not in PC mode')
        return
    else:
        # Consider using a dict here for faster lookups:
        if command in {'000080', '001B9B', '000181', '00008A', '000086', '000192', '000585', '000537', '000191', '000158',
                '0001F7', '0001C1', '000144', '000135', '00018B', '000087', '00008D', '000058', '000183', '0001BF', '000044'}:
            remote['mode'] = None
            log.debug('Disabling: Beo remote in some mode')
            return

    # Mapped codes
    if command in {'00000D', '00005C', '000036', '0000D5', '0000D9', '000035', '00001E', '00001F', '000032', '000034', '000088'}:
        pass
    else:
        log.debug('Unmapped Code: ' + command)
        return

    # Menu
    if command == '00005C':
        kodi.Input.Home()
        return

    # Stop
    if command == '000036':
        kodi.Input.Back()
        return

    ctx = getContext(kodi)
    playerObj = getPlayer(kodi)

    log.debug('Current context: ' + ctx)
    log.debug('Current player: ' + str(playerObj))

    # Mute: (vol up+down)
    if command == '00000D':
        kodi.Player.PlayPause(playerObj.get('playerid'))
        return

    # Green
    if command == '0000D5':
        kodi.Player.PlayPause(playerObj.get('playerid'))
        return

    # Red
    if command == '0000D9':
        kodi.Player.Stop(playerObj.get('playerid'))
        return

    # Go
    if command == '000035':
        if ctx in {'Fullscreen video', 'Audio visualisation'}:
            kodi.Input.ShowOSD()
        else:
            kodi.Input.Select()
        return

    # Up
    if command == '00001E':
        if ctx == 'Fullscreen video':
            kodi.Player.Seek(playerid=playerObj.get('playerid'), value=add_time(playerObj, timedelta(minutes=10)))
        else:
            kodi.Input.Up()
        return

    # Down
    if command == '00001F':
        if ctx == 'Fullscreen video':
            kodi.Player.Seek(playerid=playerObj.get('playerid'), value=sub_time(playerObj, timedelta(minutes=10)))
        else:
            kodi.Input.Down()
        return

    # Left
    if command == '000032':
        if ctx in {'Fullscreen video', 'Audio visualisation'}:
            if playerObj.get('type') == 'audio':
                kodi.Input.ExecuteAction(action='skipprevious')
            else:
                kodi.Player.Seek(playerid=playerObj.get('playerid'), value=sub_time(playerObj, timedelta(seconds=10)))
        else:
            kodi.Input.Left()
        return

    # Right
    if command == '000034':
        if ctx in {'Fullscreen video', 'Audio visualisation'}:
            if playerObj.get('type') == 'audio':
                # Next track
                kodi.Input.ExecuteAction(action='skipnext')
            else:
                # Seek 10 seconds forward
                kodi.Player.Seek(playerid=playerObj.get('playerid'), value=add_time(playerObj, timedelta(seconds=10)))
        else:
            kodi.Input.Right()
        return

    # Text
    if command == '000088':
        if ctx == 'Fullscreen video':
            if bool(kodi.Player.GetProperties(playerid=playerObj.get('playerid'),properties=['subtitleenabled'])['result']['subtitleenabled']) is True:
                kodi.Player.SetSubtitle(playerid=playerObj.get('playerid'), subtitle='off', enable=False)
                message = 'Subtitles DISABLED'
            else:
                kodi.Player.SetSubtitle(playerid=playerObj.get('playerid'), subtitle='on', enable=True)
                message = 'Subtitles ENABLED'
            kodi.GUI.ShowNotification(title='Subtitles', message=message, displaytime=1500)
        return

def worker(queue):
    '''
    Worker process which handles ir commands
    '''

    log.debug('Started worker thread')

    while True:
        if len(queue) > 0:
            item = queue.pop(0)
            try:
                ir_command(item['kodi'], item['remote'], item['command'])
            except Exception as e:
                log.debug(e)
        else:
            sleep(0.001)

def main():
    '''
    Starts the main loop
    '''

    log.info('Starting pyArduinoBeoRemote for Kodi..')

    try:
        kodi = Kodi(KODI_HOST, username=USERNAME, password=PASSWORD)

        if kodi.JSONRPC.Ping()['result'] == 'pong':
            log.info('Success: Connected to ' + KODI_HOST)
        else:
            raise('Cannot connect to Kodi')
    except:
        raise

    remote = {'mode': None}
    queue = []

    # Start worker thread
    thread = threading.Thread(target=worker, args=(queue,))
    thread.daemon = True
    thread.start()

    with open(IR_DEVICE, 'r') as ir:
        while True:
            data = ir.readline().replace('\n', '').upper()

            if data:
                queue.append({'kodi':kodi, 'remote':remote, 'command':data})
                log.debug('IR Signal: ' + data)
            else:
                sleep(0.05)


if __name__ == '__main__':
    main()
