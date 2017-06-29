from nexus_uploader.nexus import NexusRepositoryClient

try: # Python 3
    from unittest.mock import patch, Mock
except ImportError: # Python 2
    from mock import patch, Mock
from .pytest_markers import pypi_integration


def test_append_egg_hash_if_nexus_url_ok():
    nexus_client = NexusRepositoryClient('http://dummy-nexus.wtf', repo_id='pip', artifact_group='ta/ga/da', auth=('user', 'password'))
    url = 'http://dummy-nexus.wtf/content/repositories/pip/ta/ga/da/bonjour/1.2.3-SNAPSHOT/bonjour-1.2.3-SNAPSHOT-py2.py3-none-any.tar.gz'
    assert nexus_client.append_egg_hash_if_nexus_url(url) == 'http://dummy-nexus.wtf/content/repositories/pip/ta/ga/da/bonjour/1.2.3-SNAPSHOT/bonjour-1.2.3-SNAPSHOT-py2.py3-none-any.tar.gz#egg=bonjour==1.2.3-SNAPSHOT'

def test_append_egg_hash_if_nexus_url_external():
    nexus_client = NexusRepositoryClient('http://dummy-nexus.wtf', repo_id='pip', artifact_group='ta/ga/da', auth=('user', 'password'))
    url = 'http://outside.void/content/repositories/pip/ta/ga/da/bonjour/1.2.3-SNAPSHOT/bonjour-1.2.3-SNAPSHOT-py2.py3-none-any.tar.gz'
    assert nexus_client.append_egg_hash_if_nexus_url(url) == url

def test_append_egg_hash_if_nexus_url_hash_already_there():
    nexus_client = NexusRepositoryClient('http://dummy-nexus.wtf', repo_id='pip', artifact_group='ta/ga/da', auth=('user', 'password'))
    url = 'http://dummy-nexus.wtf/content/repositories/pip/ta/ga/da/bonjour/1.2.3-SNAPSHOT/bonjour-1.2.3-SNAPSHOT-py2.py3-none-any.tar.gz#egg=bonjour==1.2.3-SNAPSHOT'
    assert nexus_client.append_egg_hash_if_nexus_url(url) == url


def test_upload_from_pypi_if_need_be__with_matching_pkgs_on_nexus():
    with patch('nexus_uploader.nexus.requests') as nexus_requests:
        nexus_requests.session.return_value = MockSessionFromFixtures()
        nexus_client = NexusRepositoryClient('http://dummy-nexus.wtf', repo_id='pip', artifact_group='ta/ga/da', auth=('user', 'password'))

    nexus_artifact_url = nexus_client.upload_from_pypi_if_need_be('docutils', '0.13.1', 'http://dummy-pypi.wtf/pypi/{}/json', ('py2.py3-none-any', 'py2-none-any'))

    assert nexus_artifact_url == 'http://dummy-nexus.wtf/content/repositories/pip/ta/ga/da/docutils/0.13.1/docutils-0.13.1-py2.py3-none-any.tar.gz'

def test_upload_from_pypi_if_need_be__with_no_matching_pkgs_on_nexus():
    class MockSession404(Mock):
        def get(self, url):
            return MockRequestsResponse(status_code=404)
    mock_session = MockSession404()
    with patch('nexus_uploader.nexus.requests') as nexus_requests:
        nexus_requests.session.return_value = mock_session
        nexus_client = NexusRepositoryClient('http://dummy-nexus.wtf', repo_id='pip', artifact_group='ta/ga/da', auth=('user', 'password'))

    with patch('nexus_uploader.pypi.get_package_releases') as pypi_get_package_releases_mock:
        pypi_get_package_releases_mock.return_value = {
            '1.2.3': [
                {
                    'python_version': 'any',
                    'url': 'https://pypi.python.org/packages/5f/6d/e864b3c61b81eec57386ac62082fccfe694c7c3046d8723258a37da6d5fc/mylib-1.2.3-py2-none-any.whl',
                    'filename': 'mylib-1.2.3-py2-none-any.whl'
                },
                {
                    'python_version': 'any',
                    'url': 'https://pypi.python.org/packages/7c/30/8fb30d820c012a6f701a66618ce065b6d61d08ac0a77e47fc7808dbaee47/mylib-1.2.3-py3-none-any.whl',
                    'filename': 'mylib-1.2.3-py3-none-any.whl'
                },
                {
                    'python_version': 'source',
                    'url': 'https://pypi.python.org/packages/05/25/7b5484aca5d46915493f1fd4ecb63c38c333bd32aa9ad6e19da8d08895ae/mylib-1.2.3.tar.gz',
                    'filename': 'mylib-1.2.3.tar.gz'
                }
            ]
        }
        nexus_artifact_url = nexus_client.upload_from_pypi_if_need_be('mylib', '1.2.3', 'http://dummy-pypi.wtf/pypi/{}/json', ('py2.py3-none-any', 'py2-none-any'))

    assert nexus_artifact_url == 'http://dummy-nexus.wtf/content/repositories/pip/ta/ga/da/mylib/1.2.3/mylib-1.2.3-py2.py3-none-any.tar.gz'
    assert mock_session.post.called


class MockSessionFromFixtures(object):
    def get(self, url):
        pkg_name, version = url.split('/')[-2:]
        with open('tests/fixtures/{}-{}.html'.format(pkg_name, version), 'r') as f:
            return MockRequestsResponse(text=f.read())

class MockRequestsResponse:
    def __init__(self, status_code=200, text=''):
        self.content = self.text = text
        self.status_code = status_code
    def raise_for_status(self):
        pass
