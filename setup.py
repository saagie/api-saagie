from setuptools import setup

setup(
    name='saagieapi',
    version='0.2',
    description='Python API to interact with Saagie',
    url='git@gitlab.com/saagie-group/service/internal/api-saagie.git',
    author='Service team',
    license='GLWTPL',
    packages=['saagieapi'],
    install_requires=['requests', 'gql'],
    zip_safe=False
)
