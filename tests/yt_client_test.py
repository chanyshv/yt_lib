from tests.constants import CHAN_ID, VID_ID, COOKIES_PATH
from yt_lib.states import ActResult, SubscribeAction, LikeAction

import pytest as pt
from http.cookiejar import LWPCookieJar
import json

from tests.constants import CJ_PATH

from yt_lib import YoutubeClient


@pt.fixture(scope='module', params=['raw', 'cj'])
def cookies(request):
    if request.param == 'cj':
        cj = LWPCookieJar(CJ_PATH)
        cj.load()
        return cj, request.param
    elif request.param == 'raw':
        with open(COOKIES_PATH) as f:
            cookies = json.load(f)
        return cookies, request.param


@pt.fixture(scope='module')
def yt_client(cookies):
    cookies, c_type = cookies
    if c_type == 'raw':
        client = YoutubeClient(cookies=cookies)
    elif c_type == 'cj':
        client = YoutubeClient(cj=cookies)
    client.init_session()
    return client


@pt.fixture(params=['like', 'dislike', 'take back'])
def rate_action(request):
    if request.param == 'like':
        return LikeAction.LIKE
    if request.param == 'dislike':
        return LikeAction.DISLIKE
    if request.param == 'take back':
        return LikeAction.TAKE_BACK


@pt.fixture(params=['subscribe', 'unsubscribe'])
def subscribe_action(request):
    if request.param == 'subscribe':
        return SubscribeAction.SUBSCRIBE
    if request.param == 'unsubscribe':
        return SubscribeAction.UNSUBSCRIBE


def test_rate(yt_client, rate_action: type(LikeAction(1))):
    res = yt_client.rate(VID_ID, rate_action)
    assert res == ActResult.SUCCESS


def test_sub(yt_client):
    res = yt_client.subscribe(CHAN_ID, SubscribeAction.SUBSCRIBE)
    assert res == ActResult.SUCCESS


def test_trends(yt_client: YoutubeClient):
    trends = yt_client.get_trends()
    assert len(trends) > 1


def test_comment(yt_client: YoutubeClient):
    res = yt_client.write_comment(VID_ID, 'good video. tnx')
    assert res == ActResult.SUCCESS
