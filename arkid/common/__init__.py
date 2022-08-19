from types import SimpleNamespace

class DeepSN(SimpleNamespace):

    def dict(self):
        _data = {}
        for key,val in self.__dict__.items():
            
            if isinstance(val,DeepSN):
                _data[key] = val.dict()
            elif isinstance(val,list):
                _data[key] = [
                    item.dict() if isinstance(item,DeepSN) else item for item in val
                ]
            elif isinstance(val,dict):
                _data[key] = {}
                for k,v in val.items():
                    if isinstance(v,DeepSN):
                        _data[key][k] = v.dict()
                    elif isinstance(v,list):
                        _data[key][k] = [
                            item.dict() if isinstance(item,DeepSN) else item for item in v
                        ]
                    else:
                        _data[key][k] = v
            else:
                _data[key] = val
        return _data