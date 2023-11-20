from setuptools import setup, find_packages

setup(
    name='r809filesyncer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'syncer=r809filesyncer.syncer:main',
        ],
    },
)
