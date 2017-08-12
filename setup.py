from distutils.core import setup

setup(
    name='wx_map',
    version='0.5',
    packages=['wx_map'],
    url='https://github.com/robOcity/wx_map',
    license='MIT',
    author='Robert Osterburg',
    author_email='robert.osterburg@gmail.com',
    description=('Downloads archived weather maps from the',
                 'Weather Prediction Center (WPC).'),
    keywords=['weather', 'map', 'surface'],
    classifiers=['Topic :: Scientific/Engineering :: Atmospheric Science'],
)
