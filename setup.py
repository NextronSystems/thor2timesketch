from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()
with open("requirements.txt", "r", encoding="utf-8") as requirements_file:
    requirements = requirements_file.read().splitlines()


setup(
    name='thor_ts_mapper',
    version='0.1.1',
    keywords='thor, timesketch, mapper, converter, nextron',
    packages=find_packages(),
    url='https://github.com/NextronSystems/thor-ts-mapper.git',
    author='Ion Cicala (Nextron Systems GmbH)',
    author_email='ion.cicala@nextron-systems.com',
    description='Convert THOR security scanner logs to Timesketch format',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
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
