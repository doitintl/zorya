from google.appengine.ext import vendor
import sys
# Add any libraries installed in the "lib" folder.
vendor.add('lib')
sys.path = ['lib'] + sys.path