from enum import Enum


class ActResult(Enum):
    SUCCESS = 1
    FAIL = 2


class SubscribeAction(Enum):
    SUBSCRIBE = 1
    UNSUBSCRIBE = 2


class LikeAction(Enum):
    LIKE = 1
    DISLIKE = 2
    TAKE_BACK = 3
