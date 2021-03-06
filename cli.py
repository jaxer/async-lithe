# -*- coding: utf-8 -*-

import asyncio
import argparse
import logging

from lithe import *

async def aux_on_validate(host):
    while True:
        await aux_on(host)
        if await current_source(host) == SOURCE_AUX:
            break
        await asyncio.sleep(1)


async def aux_off_validate(host):
    while True:
        await aux_off(host)
        if await current_source(host) != SOURCE_AUX:
            break
        await asyncio.sleep(1)


async def main(args):
    host = args.host

    if args.command == 'auxOn':
        if args.toggle:
            await aux_off(host)
            await asyncio.sleep(0.2)
        await aux_on_validate(host)

    elif args.command == 'auxOff':
        if args.toggle:
            await aux_on(host)
            await asyncio.sleep(0.2)
        await aux_off_validate(host)

    elif args.command == 'status':
        parsed = await status(host)
        print(json.dumps(parsed, indent=4, sort_keys=True))

    elif args.command == 'currentSource':
        print(await current_source(host))
    

parser = argparse.ArgumentParser(description='Call Lithe API')

parser.add_argument('--toggle', action='store_true', help=
    'toggle aux on/off even if its already '
    'correctly set (used for waking up speaker)')
parser.add_argument('--verbose', '-v', action='store_true', dest='verbose')
parser.add_argument('host', help='IP of a speaker')
parser.add_argument('command', choices=[
    'auxOn', 
    'auxOff', 
    'status',
    'currentSource'])

args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

asyncio.run(main(args))
