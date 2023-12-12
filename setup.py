from distutils.core import setup

setup(
    name='camera_tools',
    python_requires='==3.10',
    author='Martin Privat',
    version='0.1.4',
    packages=['camera_tools','camera_tools.tests'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='camera tools',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy", 
        "opencv-contrib-python-rolling @ https://github.com/ElTinmar/build_opencv/raw/main/opencv_contrib_python_rolling-4.8.0.20231212-cp310-cp310-linux_x86_64.whl",
        "harvesters",
        "v4l2py"
    ]
)
