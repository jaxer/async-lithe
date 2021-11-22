# -*- coding: utf-8 -*-

import asyncio
import socket
import json
import logging

PORT = 7777

REM_ID = b'\x00\x00'
CMD_SET = b'\x02'
CMD_GET = b'\x01'
PADDING = b'\x03\x00\x00\x00\x00\xf0\x00'

SOURCE_AUX = 'Line-IN (Aux-In)'

async def write(writer, payload):
    logging.debug(f'Send: {payload!r}')
    writer.write(payload)
    await writer.drain()

async def register(ip):
    logging.debug(f'Connecting to: {ip!r}')
    reader, writer = await asyncio.open_connection(
        ip, PORT)

    hostname = socket.gethostname()

    await write(writer, REM_ID + CMD_SET + PADDING + hostname.encode())

    data = await reader.read(1024)
    logging.debug(f'Received: {data!r}')

    if len(data) <= 0:
        raise Exception('Registration failed')
    
    return reader, writer

async def disconnect(writer):
    logging.debug('Close the connection')
    writer.close()
    await writer.wait_closed()

async def auxOn(ip):
    reader, writer = await register(ip)
    await write(writer, REM_ID + CMD_SET + b'\x5f\x00\x00\x00\x00' + b'\x00\x00')
    await disconnect(writer)

async def auxOff(ip):
    reader, writer = await register(ip)
    await write(writer, REM_ID + CMD_SET + b'\x60\x00\x00\x00\x00' + b'\x00\x00')
    await disconnect(writer)

async def status(ip):
    reader, writer = await register(ip)

    try:
        await write(writer, REM_ID + CMD_SET + 
            b'\x29\x00\x00\x00\x00\x0a\x00GETUI:PLAY')
        
        while True:
            data = await reader.read(32 * 1024)
            logging.debug(f'Received: {data!r}')

            PREFIX_SIZE = 9
            HEAD = b'{"CMD ID":3,'
            HEAD_SIZE = len(HEAD)

            if len(data) > PREFIX_SIZE + HEAD_SIZE and data[
                PREFIX_SIZE + 1 : PREFIX_SIZE + 1 + HEAD_SIZE] == b'{"CMD ID":3,':
                newlineIndex = data.find(b'\n')
                assert newlineIndex > -1

                raw = data[PREFIX_SIZE + 1:newlineIndex]
                return json.loads(raw.decode())
    finally:
        await disconnect(writer)

async def currentSource(ip):
    parsed = await status(ip)
    n = parsed['Window CONTENTS']['Current Source']

    return (
        "None",
        "Airplay",
        "DMR", # 2
        "DMP",
        "Spotify",
        "USB",
        "SD-Card",
        "Melon",
        "vTuner",
        "TuneIn",
        "Miracast",
        "-",
        "MRA-Slave",
        "-",
        SOURCE_AUX, # 14
        "-",
        "Apple Device",
        "Direct URL",
        "QPlay",
        "Bluetooth",
        "-",
        "Deezer",
        "Tidal",
        "Favorites",
        "GoogleCast",
        "External source",
        "-",
        "Roon Labs",
        "Alexa"
    )[n]