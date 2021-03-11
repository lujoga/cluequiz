from setuptools import setup

setup(
    name='cluequiz',
    packages=['cluequiz'],
    include_package_data=True,
    install_requires=[
        'pygame==1.9.6',
        'pyyaml',
        'pyserial',
        'Pillow',
        'Pygments',
        'paho-mqtt',
    ],
    entry_points={
        'console_scripts': [
            'cluequiz=cluequiz.__main__:main'
        ]
    }
)
