from nexus_uploader.nexus import NexusRepositoryClient


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
