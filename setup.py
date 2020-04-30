"""ArkID Setup File"""
from __future__ import print_function
import io
import os
from fnmatch import fnmatchcase
from setuptools import convert_path, find_packages, setup
import toml

BASE_DIR = 'arkid'

# Provided as an attribute, so you can append to these instead
# of replicating them:
STANDARD_EXCLUDE = ["*.pyc", "*.bak", "CHANGELOG.md", "package.json", "package-lock.json", "settings_local.py"]

STANDARD_EXCLUDE_DIRECTORIES = [
    "CVS", "./build", ".git", ".idea", "node_modules", "EGG-INFO", "dist", "django_arkid.egg-info", "pip-egg-info",
    "*.egg-info"
]


# Copied from paste/util/finddata.py
def find_package_data(where=".", package="", exclude=None, exclude_directories=None, only_in_packages=True):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.
    The dictionary looks like::
        {"package": [files]}
    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.
    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).
    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.
    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).
    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """
    out = {}
    stack = [(convert_path(where), "", package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            file_name = os.path.join(where, name)
            if os.path.isdir(file_name):
                bad_name = False
                for pattern in exclude_directories:
                    if fnmatchcase(name, pattern) or file_name.lower() == pattern.lower():
                        bad_name = True
                        # if show_ignored:
                        #     print("Directory %s ignored by pattern %s" % (file_name, pattern), file=sys.stderr)
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(file_name, "__init__.py")) and not prefix:
                    new_package = name if not package else package + "." + name
                    stack.append((file_name, "", new_package, False))
                else:
                    stack.append((file_name, prefix + name + "/", package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if fnmatchcase(name, pattern) or file_name.lower() == pattern.lower():
                        bad_name = True
                        # if show_ignored:
                        #     print("File %s ignored by pattern %s" % (file_name, pattern), file=sys.stderr)
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out


PACKAGE_DATA = find_package_data(exclude_directories=STANDARD_EXCLUDE_DIRECTORIES, exclude=STANDARD_EXCLUDE)
LONG_DESCRIPTION = io.open(os.path.join(BASE_DIR, 'README.md'), encoding='utf-8').read()

# Dynamically calculate the version based on allauth.VERSION.
VERSION = __import__(BASE_DIR).__version__

CONTENT = toml.load(os.path.join(BASE_DIR, 'Pipfile'))['packages']
INSTALL_REQUIRES = ['{0}{1}'.format(key, value) if value != '*' else key for key, value in CONTENT.items()]

METADATA = dict(
    name='django-arkid',
    version=VERSION,
    author='LongGuiKeJi',
    author_email='bd@longguikeji.com',
    description='ArkID是全新一代企业单点登录解决方案, '
    '彻底告别企业内多系统多账号的烦恼, 节省管理成本, '
    '自带功能全面的WEB管理界面，提升管理效率。',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/longguikeji/arkid-core',
    download_url='https://github.com/longguikeji/arkid-core',
    keywords='django LDAP OAuth OpenID SAML HTTP API SSO',
    tests_require=[],
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    dependency_links=["https://mirrors.aliyun.com/pypi/simple"],
    classifiers=[
        'Development Status :: 1 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'License :: OSI Approved :: GNU License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 3.0',
    ],
    packages=find_packages(),
    package_data=PACKAGE_DATA,
    zip_safe=True,
)

if __name__ == '__main__':
    setup(**METADATA)
