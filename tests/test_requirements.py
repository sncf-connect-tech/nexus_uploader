from nexus_uploader.requirements import read_requirements, requirements2reqfile_lines


REQUIREMENTS = [
    'http://nexus/content/repositories/pip/com/vsct/pip/wrapt/1.10.6/wrapt-1.10.6-py2.py3-none-any.tar.gz',
    '-e ../luigiutils # http://nexus/content/repositories/python/com/vsc/luigiutils/1.2.3/luigiutils-1.2.3-py2.py3-none-any.tar.gz',
    'argparse==1.4.0',
    'elasticsearch>=2.2.0'
]


def test_read_requirements():
    requirements_read = read_requirements(REQUIREMENTS)
    assert len(requirements_read) == 4

def test_requirements2reqfile_lines():
    reqlines = requirements2reqfile_lines(read_requirements(REQUIREMENTS))
    assert reqlines == REQUIREMENTS
