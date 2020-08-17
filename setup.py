from setuptools import setup, find_packages

from wterm import __version__

with open('README.md', 'r') as readme:
    README = readme.read()

setup(
    name='wterm',
    version=__version__,
    author='Spriithy',
    license='gpl-3.0',
    python_requires='>=3.6',
    install_requires=[],
    packages=find_packages(),
    description='Lightweight terminal colors and logging interface',
    long_description_content_type='text/markdown',
    long_description=README,
    url='https://github.com/Spriithy/wterm/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
    keywords=[
        'terminal',
        'console',
        'logging',
        'colors',
    ],
)
