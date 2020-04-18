'''
demo for crontab plugin
'''

from oneid_meta.models import User


def maintain_admin_name():
    '''
    just demo
    '''
    print("demo")
    admin, _ = User.valid_objects.get_or_create(username='admin')
    admin.name = 'admin'
    admin.save(update_fields=['name'])


def main():
    '''
    entrypoint by convention
    '''
    maintain_admin_name()
