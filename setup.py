from setuptools import setup, find_packages


setup(
    name='python_helpers',
    version='0.1',
    packages=find_packages(),
    author='Malwin Niehus',
    author_email='niehus@hiskp.uni-bonn.de',
    description='some short helpers to simplify common tasks',
    keywords='enum string json',
    url='https://github.com/patbat/python_helpers',
    project_urls={
        'Source Code': 'https://github.com/patbat/python_helpers',
    },
    package_data={'python_helpers': ['py.typed']},
    zip_safe=False,
    classifiers=[
        'License :: MIT License'
    ]
)
