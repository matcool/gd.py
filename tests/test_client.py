# Test suite for gd.Client object.
# Will be wrapped with unittest soon.

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

import gd

client = gd.Client()


async def test():

    print('-' * 20)

    print('gd.Client Test Suite')

    cases = (
        ('ping_server',        [],                                 {}),
        ('get_song',           [810215],                           {}),
        ('get_ng_song',        [655284],                           {}),
        ('get_user',           [71],                               {}),
        ('fetch_user',         [71],                  {'stats': True}),
        ('search_user',        ['NeKitDS'],                        {}),
        ('find_user',          ['RobTop'],                         {}),
        ('get_daily',          [],                                 {}),
        ('get_weekly',         [],                                 {}),
        ('get_level',          [30029017],                         {}),
        ('get_leaderboard',    ['creators'],             {'count': 1}),
        ('get_top',            ['creators'],             {'count': 3}),
        ('test_captcha',       [],                                 {}),
        ('search_levels',      [],         {'query': 'AdventureGame'})
    )

    r = []

    for f_name, args, kwargs in cases:

        coro = getattr(client, f_name)

        r.append(coro(*args, **kwargs))

    results = await asyncio.gather(*r)

    for (f_name, args, kwargs), res in zip(cases, results):

        print('{}() -> {}'.format(f_name, res), end='\n\n')

    print('End Of Test Suite')

    print('-' * 20)


if __name__ == '__main__':
    test().run()