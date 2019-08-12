from typing import Mapping, AnyStr, List, Union, Any


def rec_find(data: Union[Mapping, List], name: AnyStr) -> Any:
    if isinstance(data, Mapping):
        for itm_name, itm in data.items():
            if isinstance(itm, Mapping) or isinstance(itm, List):
                res = rec_find(itm, name)
                if res:
                    return res
            if itm_name == name:
                return itm
    if isinstance(data, List):
        for itm in data:
            res = rec_find(itm, name)
            if res:
                return res
