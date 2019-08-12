import json
import os
import re
from copy import deepcopy
from urllib import parse
from http.cookiejar import CookieJar
from typing import Mapping, Union, AnyStr, Dict, List

import requests as rq
from bs4 import BeautifulSoup

from yt_lib.constants import CHANNEL_ULR, DEF_DATA, DEF_HEADERS, YT_URL
from yt_lib.states import ActResult, LikeAction, SubscribeAction
from yt_lib.utils import rec_find
from yt_lib.common import Video
from yt_lib.exceptions import NoCookieError


class YoutubeClient:
    """
    A YouTube client.
    Provides rates, subscribe, comments actions


    >>> from yt_lib import states
    >>> from yt_lib import YoutubeClient
    >>> client = YoutubeClient(cookies=cookies)
    >>> client.init_session()
    >>> client.subscribe('UCtinbF-Q-fVthA0qrFQTgXQ', states.SubscribeAction.SUBSCRIBE)
    <ActResult.SUCCESS: 1>
    """
    _like_action_mapper = {
        LikeAction.LIKE: 'LIKE',
        LikeAction.DISLIKE: 'DISLIKE',
        LikeAction.TAKE_BACK: 'INDIFFERENT',
    }

    _subscribe_action_mapper = {
        SubscribeAction.SUBSCRIBE: 'subscribeEndpoint',
        SubscribeAction.UNSUBSCRIBE: 'unsubscribeEndpoint',
    }

    def __init__(self, cj: CookieJar = None,
                 cookies: Mapping[str, str] = None,
                 proxies: Mapping[str, str] = None,
                 headers: Mapping[str, str] = None
                 ):
        """
        :param cj: CookieJar object to use
        :param cookies: Cookies to use. Cookies required to work: APISID,
            CONSENT, HSID, LOGIN_INFO, PREF, SAPISID, SID, SIDCC, SSID, VISITOR_INFO1_LIVE
        :param proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy. In requests proxies format.
        :param headers: Headers to use
        """
        if not (cj or cookies):
            raise NoCookieError('No cookie provided')
        cj = cj or rq.utils.cookiejar_from_dict(cookies)
        self.session = rq.Session()
        self.session.cookies = cj
        self.session.proxies = proxies
        self.session.headers = headers or DEF_HEADERS
        self.xsrf_token: AnyStr = ''

    def _rq_build(self, data) -> Mapping[str, Union[str, Mapping]]:
        build = deepcopy(DEF_DATA)
        build.update(data)
        return build

    def _rq_make(self,
                 name: str,
                 sej: Mapping,
                 init_data: Mapping,
                 data: Dict = None
                 ) -> Union[type(ActResult(1)), rq.Response]:
        if not self.xsrf_token:
            raise RuntimeError('Session not initialized. Call init_session first.')
        if not data:
            data = {}
        sej_str = json.dumps(self._rq_build(sej))
        data.update(
            {
                'sej': sej_str,
                'session_token': self.xsrf_token,
                'csn': init_data['csn'],
            })
        try:
            return self.session.post(
                os.path.join(YT_URL, 'service_ajax'),
                params={'name': name},
                data=data)
        except rq.RequestException:
            return ActResult.FAIL

    def subscribe(self, channel_id: str, action: type(SubscribeAction(1)), attempts: int = 1) -> type(ActResult(1)):
        """
        Subscribe/unsubscribe to any channel by id
        :param channel_id: Id of channel to subscribe/unsubscribe
        :param action: Type of subscribe
        :param attempts: (optional) Attempts of subscribe
        """
        page_html = self.session.get(parse.urljoin(CHANNEL_ULR, channel_id)).text
        init_data = self._get_init_data(page_html)
        sej_data = {
            'subscribeEndpoint': {'channelIds': [channel_id]},
            'clickTrackingParams': init_data['click_params'],
        }
        action = self._subscribe_action_mapper[action]
        for _ in range(attempts):
            r = self._rq_make(action, sej_data, init_data)
            if '"subscribed":true' in r.text:
                return ActResult.SUCCESS
            continue
        return ActResult.FAIL

    def rate(self, video_id: AnyStr, action: type(LikeAction(1)), attempts: int = 1) -> type(ActResult(1)):
        """
        Rates (like/dislike) video by id
        :param video_id: Id of video
        :param action: Type of rate
        :param attempts: (optional) Attempts of rate
        """
        page_html = self.session.get(url=parse.urljoin(YT_URL, 'watch'), params={'v': video_id}).text
        init_data = self._get_init_data(page_html)
        status = self._like_action_mapper[action]
        sej_data = {
            'likeEndpoint': {'status': status, 'target': {'videoId': video_id}},
            'clickTrackingParams': init_data['click_params']
        }
        for _ in range(attempts):
            r = self._rq_make('likeEndpoint', sej_data, init_data)
            if '"code":"SUCCESS"' in r.text:
                return ActResult.SUCCESS
            continue
        return ActResult.FAIL

    def write_comment(self, video_id: AnyStr, comment_text: AnyStr, attempts: int = 1) -> type(ActResult(1)):
        """
        Write a comment to video
        :param video_id: Id of video
        :param comment_text: Text of comment
        :param attempts: (optional) Attempts of act
        """
        page_html = self.session.get(url=parse.urljoin(YT_URL, 'watch'), params={'v': video_id}).text
        init_data = self._get_init_data(page_html)
        comm_token = self._get_comments_token(init_data['cont'])
        cej_data = {
            'createCommentEndpoint': {'createCommentParams': comm_token},
            'clickTrackingParams': init_data['click_params'],
        }
        data = {
            'comment_text': comment_text,
        }
        for _ in range(attempts):
            r = self._rq_make('createCommentEndpoint', cej_data, init_data, data)
            if comment_text in r.text:
                return ActResult.SUCCESS
            return ActResult.FAIL


    def get_trends(self) -> List[Video]:
        """
        Get videos from trends.
        """
        url = parse.urljoin(YT_URL, 'feed/trending')
        params = {'pbj': 1}
        r = self.session.get(url, params=params)
        videos = self._parse_for_video(r.json())
        return videos

    def init_session(self):
        """
        Init the session. Necessary for the correct operation of all methods.
        """
        html_txt = self.session.get(YT_URL).text
        page_soup = BeautifulSoup(html_txt, 'html.parser')
        self.xsrf_token = re.findall("XSRF_TOKEN\W*(.*)=", html_txt, re.IGNORECASE)[0].split('"')[0] + '='
        scripts = page_soup('script')
        data_script_second = next(
            iter(filter(lambda tag: tag.string and 'ID_TOKEN' in tag.string, scripts)))
        script_str = str(data_script_second.string)
        data_str = script_str[script_str.index('({') + 1:script_str.index('})') + 1]
        json_data = json.loads(data_str)
        header_id = json_data['ID_TOKEN']
        self.session.headers.update({
            'x-youtube-identity-token': header_id,
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20190809.04.02',
        })

    @classmethod
    def _parse_for_video(cls, data: Mapping) -> List[Video]:
        items = data[1]['response']['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer'] \
            ['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['shelfRenderer'] \
            ['content']['expandedShelfContentsRenderer']['items']
        videos = []
        for item in items:
            item = item['videoRenderer']
            video_id = item['videoId']
            thumbnail_url = item['thumbnail']['thumbnails'][0]['url']
            title = item['title']['simpleText']
            videos.append(Video(title, video_id, thumbnail_url))

        return videos

    @classmethod
    def _get_init_data(self, html_txt: AnyStr) -> Mapping[str, str]:
        page_soup = BeautifulSoup(html_txt, 'html.parser')
        scripts = page_soup('script')
        data_script_first = next(
            iter(filter(lambda tag: tag.string and 'window["ytInitialData"]' in tag.string, scripts)))
        data_str = str(data_script_first.string).strip(' \n')
        raw_data = data_str[data_str.index('=') + 1: data_str.index('\n')].strip(';')
        json_data = json.loads(raw_data)
        cont = rec_find(json_data, 'continuation')
        cns_token = json_data['responseContext']['webResponseContextExtensionData']['ytConfigData']['csn']
        tracking_token = json_data['trackingParams']

        data = {
            'csn': cns_token,
            'click_params': tracking_token,
            'cont': cont,
        }
        return data

    def _get_comments_token(self, cont: AnyStr) -> AnyStr:
        params = {
            'action_get_comments': 1,
            'pbj': 1,
            'ctoken': cont,
        }
        data = {'session_token': self.xsrf_token}
        r = self.session.post(parse.urljoin(YT_URL, 'comment_service_ajax'), params=params, data=data)
        find_data = r.json()['response']['continuationContents']['itemSectionContinuation']['header'] \
            ['commentsHeaderRenderer']['createRenderer']['commentSimpleboxRenderer']['submitButton'] \
            ['buttonRenderer']['serviceEndpoint']
        return rec_find(find_data, 'createCommentParams')
