from setuptools import find_packages, setup

setup(
    name='generativeMusic',
    packages=find_packages(),
    include_package_data=True,
    version='0.1.0',
    description='Create a neural network to generate sheet music',
    author='Noel Rajan',
    license='MIT',
    install_requires=[
        'keras',
        'numpy',
        'h5py',
        'music21',
        'click',
        'tensorflow'
    ],
    zip_safe=False
)
