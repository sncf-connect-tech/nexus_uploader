import random, requests, sys
from nexus_uploader.pypi import extract_classifier_and_extension, get_package_releases

# USAGE: PYTHONPATH=. ipython3 --pdb tests/smoke_test_extract_classifier_and_extension.py 100
# AUTHOR: Lucas Cimon

def main(random_releases_count):
    print('# Extracting classifier & extension from {} packages randomly picked on Pypi (no output means OK)'.format(random_releases_count))
    for pkg_name, _, pkg_release in random_packages_releases(random_releases_count):
        print(pkg_name)
        classifier, extension = extract_classifier_and_extension(pkg_name, pkg_release['filename'])
        print('{0:<70} -> {1:<30} {2}'.format(pkg_release['filename'], classifier, extension))

def random_packages_releases(random_releases_count):
    all_pypi_packages = get_all_pypi_packages()
    i = 0
    while i < random_releases_count:
        pkg_name = random.choice(all_pypi_packages)
        try:
            pkg_releases = get_package_releases(pkg_name)
        except requests.HTTPError:
            print('!!! WARNING: No release found for package name ', pkg_name)
            continue
        version = random.choice(list(pkg_releases.keys()))
        version_pkg_releases = pkg_releases[version]
        if version_pkg_releases:
            i += 1
            yield pkg_name, version, random.choice(version_pkg_releases)

def get_all_pypi_packages():
    """
    HTML structure at /simple/ :
        <html><head><title>Simple Index</title><meta name="api-version" value="2" /></head><body>
        <a href='199fix'>199Fix</a><br/>
        ...
        <a href='zzzfs'>zzzfs</a><br/>
        </body></html>
    """
    response = requests.get('https://pypi.python.org/simple/')
    response.raise_for_status()
    all_lines = [line.decode('ascii') for line in response.iter_lines()][1:-1]
    return [line[9:line.index("'", 9)] for line in all_lines]

if __name__ == '__main__':
    main(int(sys.argv[1]))
