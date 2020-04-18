'''
demo for crontab plugin
'''

from oneid_meta.models import User


def maintain_admin_name_plugin():
    '''
    just demo
    '''
    admin, _ = User.valid_objects.get_or_create(username='admin')
    admin.name = 'admin'
    admin.save(update_fields=['name'])
