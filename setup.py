from setuptools import setup

setup(
    name='querySaagieApi',
    version='0.1',
    description='Python API to interact with Saagie',
    url='git@gitlab.saagie.tech:42/service/api-saagie.git',
    author='Service team',
    license='GLWTPL',
    packages=['querySaagieApi'],
    install_requires=[
          'requests'
      ],
    zip_safe=False
)