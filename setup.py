import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_purchase',
    version='0.1',
    packages=find_packages(exclude=['tests', 'loader_tests']),
    include_package_data=True,
    license='BSD License',  # example license
    description='A purchase solution.',
    long_description=README,
    url='https://juan.sebastian.goldberg.iamsoft.org/',
    author='Juan Sebastian Goldberg',
    author_email='sebas.goldberg@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django',
        # @todo
        #'django_conditions==0.1',
        'pulp',
        ]
    # @todo
    # dependency_links=[
        #'https://github.com/sebasgoldberg/django_conditions/tarball/master#egg=django_conditions-0.1'
        #]
)
