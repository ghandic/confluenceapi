from setuptools import setup

setup(name='confluenceapi',
      version='0.1',
      description='Python package for updating confluence pages',
      keywords='confluence api atlassian jira automated',
      url='https://github.com/ghandic/confluenceapi',
      author='Andy Challis',
      author_email='andrewchallis@hotmail.co.uk',
      license='MIT',
      packages=['confluenceapi'],
      zip_safe=True,
      install_requires=[
          'pandas',
      ],)
