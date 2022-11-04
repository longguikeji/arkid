from arkid.core.event import Event, dispatch_event,CACHE_GET,CACHE_SET
from django.core.cache import cache

def get(tenant,key,**kwargs):
    rs = dispatch_event(Event(tag=CACHE_GET, tenant=tenant,data={"key":key,**kwargs}))
    for useless,(response,useless) in rs:
        if not response:
            continue
        return response
    
    return cache.get(key)

def set(tenant,key,value,**kwargs):
    rs = dispatch_event(Event(tag=CACHE_SET, tenant=tenant,data={"key":key,"value":value,**kwargs}))
    for useless,(response,useless) in rs:
        if not response:
            continue
        return response
    
    return cache.set(key,value,timeout=kwargs['expired'] if hasattr(kwargs, 'expired') else None)