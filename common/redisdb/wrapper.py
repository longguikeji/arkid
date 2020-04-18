# coding: utf-8

import cPickle
import marshal
import inspect
import redis
import simplejson
import zlib

from .connection import get_conn
from ...common.utils.serializer import CustomizedJSONSerializer


class RedisWrapper(object):

    def __init__(self, func, key_format, redis_config,
                 expire_seconds=None, compressor=None,
                 serializer=CustomizedJSONSerializer,
                 fallback_serializers=None,
                 is_refresh=False):
        # @TODO static method and class method are not supported
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.func = func
        self.key_format = key_format
        self.redis_config = redis_config
        self.expire_seconds = expire_seconds
        self.compressor = compressor() if compressor else None  # Allow no compressor
        self.serializer = serializer()  # Always need a serializer
        if fallback_serializers is None:
            self.fallback_serializers = []
        else:
            self.fallback_serializers = [s() for s in fallback_serializers]
        self.outer_caller = None
        self.is_refresh = is_refresh

    def __get__(self, instance, owner):
        # This can make it decorate method inside classes
        self.outer_caller = instance
        return self

    def __call__(self, *fn_args, **fn_kargs):
        return self._execute_func(self.is_refresh, *fn_args, **fn_kargs)

    def _execute_func(self, refresh, *fn_args, **fn_kargs):
        key = self._get_key(*fn_args, **fn_kargs)
        r = get_conn(self.redis_config)
        if not refresh:
            data = r.get(key)
            if data is not None:
                return self._decode_data(data)

        data = self.call(*fn_args, **fn_kargs)
        if data is not None:
            redis_data = self._encode_data(data)
            if self.expire_seconds:
                r.setex(key, redis_data, self.expire_seconds)
            else:
                r.set(key, redis_data)
        else:
            r.delete(key)
        return data

    def refresh(self, *fn_args, **fn_kargs):
        """Refresh data in cache with new data
        """
        return self._execute_func(True, *fn_args, **fn_kargs)

    def delete(self, *fn_args, **fn_kargs):
        """Delete data in cache
        """
        r = get_conn(self.redis_config)
        key = self._get_key(*fn_args, **fn_kargs)
        r.delete(key)

    def call(self, *fn_args, **fn_kwargs):
        """Call function directly without cache support,
        it will not put the result into cache"""
        if self.outer_caller:
            data = self.func(self.outer_caller, *fn_args, **fn_kwargs)
        else:
            data = self.func(*fn_args, **fn_kwargs)
        return data

    def _get_key(self, *fn_args, **fn_kargs):
        params = {}
        arg_spec = inspect.getargspec(self.func)
        if arg_spec.defaults:
            params.update(dict(zip(arg_spec.args[-len(arg_spec.defaults):],
                                   arg_spec.defaults)))
        if self.outer_caller:
            fn_args = [self.outer_caller, ] + list(fn_args)
        params.update(dict(zip(self.func.func_code.co_varnames, fn_args)))
        params.update(fn_kargs)
        return self.key_format % params

    def _encode_data(self, data):
        serialized_string = self.serializer.dumps(data)
        if self.compressor:
            serialized_string = self.compressor.compress(serialized_string)
        return serialized_string

    def _decode_data(self, data):
        try:
            serialized_data = data
            if self.compressor:
                serialized_data = self.compressor.decompress(serialized_data)
            return self.serializer.loads(serialized_data)
        except Exception, e:
            for candidate_serializer in self.fallback_serializers:
                try:
                    return candidate_serializer.loads(serialized_data)
                except:
                    pass
            raise e
