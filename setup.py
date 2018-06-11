from setuptools import setup, find_packages
import os

version = '1.2'
auction_core = 'openprocurement.auctions.core.includeme:includeme'
auction_transferring = 'openprocurement.auctions.core.plugins.transferring.includeme:includeme'

entry_points = {
    'openprocurement.api.plugins': [
        'auctions.core = {}'.format(auction_core)
    ],
    'openprocurement.tests': [
        'auctions.core = openprocurement.auctions.core.tests.main:suite'
    ],
    'transferring': [
        'auctions.transferring = {}'.format(auction_transferring)
    ]
}
requires = [
    'setuptools',
    'openprocurement.api',
    'openprocurement.schemas.dgf',
    'schematics-flexible'
]
test_requires = requires + []

setup(name='openprocurement.auctions.core',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/openprocurement/openprocurement.auctions.core',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.auctions'],
      include_package_data=True,
      zip_safe=False,
      extras_require={'test': test_requires},
      install_requires=requires,
      test_requires=test_requires,
      entry_points=entry_points,
      )
