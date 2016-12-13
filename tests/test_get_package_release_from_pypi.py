from nexus_uploader.pypi import get_package_release_from_pypi

# USAGE: PYTHONPATH=. py.test tests/test_get_package_release_from_pypi.py
# AUTHOR: Lucas Cimon


def test_docutils(httpserver):
    with open('tests/fixtures/pypi_docutils_2016-12-13.json', 'r') as mocked_response_content:
        httpserver.serve_content(mocked_response_content.read())
    get_package_release_from_pypi('docutils', '0.13.1', httpserver.url + '/{}/json', allowed_classifiers=('py3-none-any',))
