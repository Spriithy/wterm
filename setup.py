from setuptools import setup, find_packages

with open('requirements.txt') as reqs:
    requirements = reqs.readlines()

setup(
    name='wterm',
    version='0.0.1',
    author='Spriithy',
    python_requires='>=3.6',
    install_requires=requirements,
    packages=find_packages(),
    description='Lightweight terminal colors and logging interface',
    url='https://github.com/Spriithy/wterm/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
)
