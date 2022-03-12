from setuptools import setup

setup(
    name='kktools',  # package name
    version='1.0',  # version
    author='Konstantin Khorev',
    author_email='khorevkp@gmail.com',
    description='Tools for finance and treasury specialists',  # short description
    url='https://github.com/khorevkp/KK_Tools',  # package URL
    install_requires=['pandas'],  # list of packages this package depends on
    packages=setuptools.find_packages(exclude=['tests*']),
)