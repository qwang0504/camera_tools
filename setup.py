from distutils.core import setup

setup(
    name='camera_tools',
    author='Martin Privat',
    version='0.1.3',
    packages=['camera_tools','camera_tools.tests'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='camera tools',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy", 
        "opencv-python",
        "harvesters",
        "v4l2py"
    ]
)