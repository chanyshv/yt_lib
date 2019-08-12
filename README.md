yt_lib: Young YouTube library
==========================
yt_lib is the unofficial library for YouTube, which supports operations with likes, subscriptions, comments.
```
>>> from yt_lib import states
>>> from yt_lib import YoutubeClient
>>> client = YoutubeClient(cookies=cookies)
>>> client.init_session()
>>> client.subscribe('UCtinbF-Q-fVthA0qrFQTgXQ', states.SubscribeAction.SUBSCRIBE)
<ActResult.SUCCESS: 1>
```
Feature Support
---------------
The library begins to take its first steps, so the list is small.
- Rates (like, dislikes and take back)
- Subscriptions (and unsubscribes)
- Writing comments

Installation
------------
To install yt_lib, use pip
``` {.sourceCode .bash}
$ will be soon...
```
Documentation
-------------
Will be soon...
