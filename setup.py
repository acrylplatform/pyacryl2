from setuptools import setup, find_packages

url = "https://github.com/DPInvaders/pyacryl2"

packages = find_packages(exclude=["tests", "tests.*"])

install_requires = [
    'aiohttp==3.5.4',
    'base58==1.0.3',
    'mnemonic==0.18',
    'pysha3==1.0.2',
    'python-axolotl-curve25519==0.4.1.post2',
    'requests==2.21.0',
    'ujson==1.35',
]

keywords = 'acryl pyacryl api client async'
python_version = '>=3.6.0'


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyacryl2',
    version='0.1.4',
    packages=packages,
    install_requires=install_requires,
    test_suite="tests",
    url=url,
    keywords=keywords,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author='DPInvaders',
    author_email='dima@acrylplatform.com',
    description='Acryl node API client',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
