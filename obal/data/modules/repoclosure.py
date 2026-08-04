#!/usr/bin/python
"""
Run repoclosure on a set of repositories
"""

from subprocess import check_output, CalledProcessError, STDOUT
from ansible.module_utils.basic import AnsibleModule


def build_command(config, check, additional_repos=None, lookaside=None, arch=None,
                  exclude_repos=None, exclude_packages=None):
    """
    Build the `dnf repoclosure` command line for the given set of repositories
    """
    additional_repos = additional_repos or []
    lookaside = lookaside or []
    arch = arch or ['noarch', 'x86_64']
    exclude_repos = exclude_repos or []
    exclude_packages = exclude_packages or []

    command = [
        'dnf',
        'repoclosure',
        '--refresh',
        '--newest',
        '--best',
        '--config',
        config
    ]

    for one_arch in arch:
        command.extend(['--arch', one_arch])

    for name in check:
        command.extend(['--check', name])
        command.extend(['--repo', name])

    for repo in additional_repos:
        command.extend(['--repofrompath', '{},{}'.format(repo['name'], repo['url'])])

    for repo in lookaside:
        command.extend(['--repo', repo])

    # Exclude the package(s) under test from specific (e.g. persistent staging)
    # repos, so a stale sibling build there (e.g. a self-pinned "-doc"
    # subpackage requiring "%{name} = %{version}-%{release}") isn't flagged as
    # broken once a newer build of the same package supersedes it elsewhere.
    # Other repos are left untouched, so real cross-package regressions
    # (a different package still capping this one below its new version)
    # keep failing loudly.
    for repo in exclude_repos:
        for package in exclude_packages:
            command.append('--setopt={}.excludepkgs={}'.format(repo, package))

    return command


def main():
    """
    Run repoclosure on a set of repositories
    """
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(type='str', required=True),
            check=dict(type='list', required=True),
            additional_repos=dict(type='list', required=False, default=[]),
            lookaside=dict(type='list', required=False, default=[]),
            arch=dict(type='list', required=False, default=['noarch', 'x86_64']),
            exclude_repos=dict(type='list', required=False, default=[]),
            exclude_packages=dict(type='list', required=False, default=[]),
        )
    )

    command = build_command(
        config=module.params['config'],
        check=module.params['check'],
        additional_repos=module.params['additional_repos'],
        lookaside=module.params['lookaside'],
        arch=module.params['arch'],
        exclude_repos=module.params['exclude_repos'],
        exclude_packages=module.params['exclude_packages'],
    )

    try:
        output = check_output(command, universal_newlines=True, stderr=STDOUT)
    except CalledProcessError as error:
        module.fail_json(msg='Repoclosure failed', command=' '.join(command), output=error.output)

    module.exit_json(changed=False, output=output)


if __name__ == '__main__':
    main()
