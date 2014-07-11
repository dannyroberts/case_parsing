from setuptools import setup

setup(
    name='case_parsing',
    version='0.0.0',
    author='Dimagi, Inc.',
    author_email='droberts@dimagi.com',
    description='Library for parsing CommCare Case XML 2.0',
    url='',
    packages=['case_parsing'],
    install_requires=[
        'iso8601',
        'jsonobject',
        'xml2json==0.0.0',
    ],
    dependency_links=[
        'git+https://github.com/dimagi/xml2json#egg=xml2json-0.0.0',
    ],
    tests_require=['unittest2', 'nose'],
    test_suite='test',
)
