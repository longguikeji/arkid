'''
demo for crontab plugin
'''
from celery import shared_task


@shared_task
def helloword_plugin():
    '''
    just demo
    '''
    print("Hello ArkID")
