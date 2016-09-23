from nexus_uploader.pypi import extract_classifier_and_extension
try:
    import pytest
    xfail = pytest.mark.xfail
except ImportError:
    xfail = lambda f: f  # dummy decorator

# USAGE: PYTHONPATH=. py.test tests/test_extract_classifier_and_extension.py
# AUTHOR: Lucas Cimon

def test_no_classifier():
    classifier, extension = extract_classifier_and_extension('luigi', 'luigi-1.1.1.tar.gz')
    assert extension == 'tar.gz'
    assert classifier == 'py2.py3-none-any'

def test_osx_targz():
    classifier, extension = extract_classifier_and_extension('luigi', 'luigi-1.0.9.macosx-10.7-intel.tar.gz')
    assert extension == 'tar.gz'
    assert classifier == 'macosx-10.7-intel'

def test_windows_wheel():
    classifier, extension = extract_classifier_and_extension('tornado', 'tornado-4.3b2-cp35-none-win32.whl')
    assert extension == 'whl'
    assert classifier == 'cp35-none-win32'

def test_maven_snapshot_package():
    classifier, extension = extract_classifier_and_extension('logdorak', 'logdorak-1.0-SNAPSHOT-py2.py3-none-any.tar.gz')
    assert extension == 'tar.gz'
    assert classifier == 'py2.py3-none-any'

@xfail
def test_incorrect_package_name1():
    classifier, extension = extract_classifier_and_extension('asv_media', 'asv_media-dev-20121101-01.tar.gz')
    assert extension == 'tar.gz'
    assert classifier == 'py2.py3-none-any'

@xfail
def test_incorrect_package_name2():
    classifier, extension = extract_classifier_and_extension('freetype', 'Freetype-Milestone1-py2.4-win32.egg')
    assert extension == 'tar.gz'
    assert classifier == 'py2.4-none-win32'

@xfail
def test_incorrect_platform_detection():
    classifier, extension = extract_classifier_and_extension('rawphoto', 'rawphoto-0.3.0.linux-x86_64.tar.gz')
    assert extension == 'tar.gz'
    assert classifier == 'py2.py3-none-linux-x86_64'
    classifier, extension = extract_classifier_and_extension('maltfy', 'maltfy-v0.3.2.linux-i686.tar.gz')
    assert extension == 'tar.gz'
    assert classifier == 'py2.py3-none-linux-i686'
    classifier, extension = extract_classifier_and_extension('mathtools', 'mathtools-1.2.win-amd64.exe')
    assert extension == 'tar.gz'
    assert classifier == 'py2.py3-none-win-amd64'

@xfail
def test_incorrect_python_tag_detection():
    classifier, extension = extract_classifier_and_extension('instatrace', 'instatrace-1.0.0-py2.6.egg')
    assert extension == 'tar.gz'
    assert classifier == 'py2.6-none-any'
    classifier, extension = extract_classifier_and_extension('zc.recipe.zope3checkout', 'zc.recipe.zope3checkout-1.2-py2.4.egg')
    assert extension == 'tar.gz'
    assert classifier == 'py2.4-none-any'
