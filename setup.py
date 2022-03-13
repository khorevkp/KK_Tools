from setuptools import setup

setup(
    name='kktools',
    version='1.4',
    author='Konstantin Khorev',
    author_email='khorevkp@gmail.com',
    description='Tools for finance and treasury specialists',
    url='https://github.com/khorevkp/KK_Tools',
    install_requires=['pandas', 'requests'],
    packages=['kktools']
)
