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
================================
To install yt_lib, simply run this simple command in your terminal of choice:

    $ pip install yt_lib


yt_lib is actively developed on GitHub, where the code is [always available](https://github.com/hairygeek/yt_lib).

You can either clone the public repository:

    $ git clone https://github.com/hairygeek/yt_lib.git

Quickstart
================================

First make sure thar yt_lib is installed.

Let's get started with some simple examples.

Subscribes
----------
Begin by importing the ``yt_lib`` and ``yt_lib.states`` modules:

```
>>> import yt_lib
>>> from yt_lib import states
```

Now let's create YouTubeClient, this requires youtube cookies. Cookies required to work: apisid,
consent, hsid, login_info, pref, sapisid, sid, sidcc, ssid, visitor_info1_live. Imagine that we already have them:

```
>>> client = YoutubeClient(cookies=cookies)
```

Now let's initialize the session. Nothing will work without it:

```
>>> client.init_session()
```

Now we can subscribe to the channel. for this we need a type of subscription (unsubscribe / subscription), we will take it from the module ``states``:

```
>>> client.subscribe('UCtinbF-Q-fVthA0qrFQTgXQ', states.SubscribeAction.SUBSCRIBE)
    <ActResult.SUCCESS: 1>
```

We got an response. In our case, this is SUCCESS, which means that the subscription was successful.

Rates
--------------------
In the same way we can like:

```
>>> client.rate('V6Y-ahQFQDA', states.LikeAction.LIKE)
    <ActResult.SUCCESS: 1>
```

or dislike:

```
>>> client.rate('V6Y-ahQFQDA', states.LikeAction.DISLIKE)
    <ActResult.SUCCESS: 1>
```

or take action back:

```
>>> client.rate('V6Y-ahQFQDA', states.LikeAction.TAKE_BACK)
    <ActResult.SUCCESS: 1>
```

That's not all, but l'm too lazy to describe the rest. See the description of methods.



