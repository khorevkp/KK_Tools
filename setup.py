from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='kktools',
    version='3.6.1',  # Consider updating the version number
    author='Konstantin Khorev',
    author_email='khorevkp@gmail.com',
    description='Tools for finance and treasury specialists',
    url='https://github.com/khorevkp/KK_Tools',
    install_requires=[
        'lxml>=4.9.3',
        'openpyxl>=3.1.2',
        'pandas>=2.1.1',
        'requests>=2.31.0'
    ],
    packages=find_packages(),  # Automatically discover all packages in your project
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',  # Specify minimum Python version
)
