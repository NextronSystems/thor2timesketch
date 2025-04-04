from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()


setup(
    name='thor_ts_mapper',
    version='0.1.1',
    keywords='thor, timesketch, mapper, converter, nextron',
    packages=find_packages(),
    url='TBD',
    author='Ion Cicala (Nextron Systems GmbH)',
    author_email='ion.cicala@nextron-systems.com',
    description='Convert THOR security scanner logs to Timesketch format',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'thor2ts=thor_ts_mapper.__main__:main',
        ],
    },

)
