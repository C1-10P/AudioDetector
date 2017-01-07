from setuptools import setup, find_packages

setup(
    name='audio_detector',
    version='0.1',
    description='Classification of signals to detect sounds',
    url="https://github.com/C1-10P/BabyMonitor.git",
    author='C1-10P (fork author), Damian Nowok (original author)',
    author_email="C1-10P@users.noreply.github.com",
    license='GPL',
    packages=find_packages(),
    install_requires=['numpy', 'pyaudio', 'matplotlib', 'six'],
    tests_require=['pytest', "unittest2"],
    scripts=[],
    py_modules=["audio_detector"],
    include_package_data=True,
    zip_safe=False
)
