'''
create mock company for dev
'''
import django
django.setup()

from ...oneid_meta.models import Dept


def create_top_company():
    root = Dept.objects.get(uid='root')
    if not Dept.valid_objects.filter(parent=root).exists():
        print("create top company")
        Dept.valid_objects.create(uid='company', name='公司', parent=root)


def main():
    '''
    :note: 所有方法需保证幂等
    '''
    create_top_company()


if __name__ == "__main__":
    main()
