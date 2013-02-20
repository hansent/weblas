from setuptools import setup
import shutil

import plasio

# Get text from README.txt
try:
    readme_text = file('README.md', 'rb').read()
except:
    readme_text = "See documentation at plas.io"


setup(name          = 'plasio',
      version       = plasio.__version__,
      description   = 'Python LiDAR server',
      license       = 'BSD',
      keywords      = 'gis lidar las',
      author        = 'Thomas Hansen',
      author_email  = 'thomas@fresklabs.com',
      url   = 'https://github.com/grantbrown/laspy',
      long_description = '''Some descriptoin''',
      packages      = ['plasio', ],
      install_requires = ['numpy', 'psycopg2'],
      test_suite = 'test.test_plas',
      # data_files = [("laspytest/data", ["simple.las", "simple1_3.las", "simple1_4.las"])], 
      data_files = [], 
      include_package_data = True,
      zip_safe = False,
      entry_points = {'console_scripts':[
                                        ]},

      classifiers   = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS'
        ],
)

