# -*- coding: utf-8 -*-

import os
import sys

# SAE environment support
import sae

from nook import wsgi


# Insert extra library if the bundle exists
APP_ROOT = os.path.dirname(__file__)
EXTRA_LIBS_BUNDLE = 'libs.bundle.zip'
EXTRA_LIBS_BUNDLE = os.path.join(APP_ROOT, EXTRA_LIBS_BUNDLE)

if os.path.exists(EXTRA_LIBS_BUNDLE):
    sys.path.insert(0, EXTRA_LIBS_BUNDLE)

# Create the web application
application = sae.create_wsgi_app(wsgi.application)
