from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='wrchartools',
      version=version,
      description="Character and output tools",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author="Pamela McA'Nulty",
      author_email='pamela@webreply.com',
      url='webreply.com/wrchartools',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
