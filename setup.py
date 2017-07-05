import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requirements = [
    'kombu',
    'django',
]

setup_requirements = [
    'pytest-runner'
]

test_requirements = [
    'django-dynamic-fixture',
    'ipdb',
    'pytest-pep8',
    'pytest-django',
    'pytest-mock',
    'pytest-catchlog',
    'pytest-env',
    'pytest',   # keep last to avoid setuptools bug
]

extras_requirements = {
    'dev': [
        'ipdb',
    ]
}

setup(
    name='django-history',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    description='Track data changes to Django models',
    long_description=README,
    install_requires=requirements,
    zip_safe=False,
    extras_require=extras_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    url='https://github.com/xyngular/django-history',
    author='Marc Moody',
    author_email='marc.moody@xyngular.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
