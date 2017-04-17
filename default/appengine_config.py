import os
from google.appengine.ext import vendor

on_appengine = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
if on_appengine and os.name == 'nt':
    os.name = None

    import imp
    import os.path
    import inspect
    from google.appengine.tools.devappserver2.python import sandbox

    sandbox._WHITE_LIST_C_MODULES.extend(['_ssl', '_socket', '_ctypes', '_winreg',])
    # Use the system socket.

    real_os_src_path = os.path.realpath(inspect.getsourcefile(os))
    psocket = os.path.join(os.path.dirname(real_os_src_path), 'socket.py')
    imp.load_source('socket', psocket)


# Add any libraries installed in the "lib" folder.
vendor.add('lib')

DATA_BACKEND = 'datastore'
PROJECT_ID = 'polygonfm-rating-dangae'