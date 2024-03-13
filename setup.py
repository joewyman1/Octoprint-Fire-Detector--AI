from setuptools import setup

setup(
    name='OctoPrint-FireDetection',
    version='0.1.0',
    packages=['fire_detection'],
    include_package_data=True,
    entry_points={
        'octoprint.plugin': [
            'fire_detection = fire_detection:FireDetectionPlugin'
        ]
    },
    install_requires=[
        'octoprint',
    ],
    python_requires='>=3,<4',
    author='Joseph Wyman',
    author_email='mail@jooewymancode.com',
    url='https://github.com/joewyman1/Octoprint-Fire-Detector--AI',
    description='OctoPrint plugin for fire detection using AI',
    license='All Rights Reserved',
    classifiers=[
	'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
