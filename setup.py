from setuptools import setup, find_packages

setup(
    name='saagieapi',
    version='0.2.1',
    description='Python API to interact with Saagie',
    url='git@gitlab.com/saagie-group/service/internal/api-saagie.git',
    author='Service team',
    license='GLWTPL',
    packages=find_packages(),
    install_requires=['requests', 'gql'],
    zip_safe=False
)
