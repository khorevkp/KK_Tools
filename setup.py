from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='kktools',
    version='2.5',
    author='Konstantin Khorev',
    author_email='khorevkp@gmail.com',
    description='Tools for finance and treasury specialists',
    url='https://github.com/khorevkp/KK_Tools',
    install_requires=['pandas', 'requests', 'lxml'],
    packages=['kktools'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
