import logging
import platform
import venv

from . import external_commands, overrides, server

logger = logging.getLogger(__name__)


def build_wheel(ctx, req_type, req, resolved_name, why, sdist_root_dir, build_dependencies):
    logger.info('building wheel for %s', resolved_name)
    builder = overrides.find_override_method(req.name, 'build_wheel')
    if not builder:
        builder = _default_build_wheel
    wheel_filenames = builder(ctx, req_type, req, resolved_name, why, sdist_root_dir,
                              build_dependencies)
    for wheel in wheel_filenames:
        server.add_wheel_to_mirror(ctx, sdist_root_dir.name, wheel)
    ctx.add_to_build_order(req_type, req, resolved_name, why)
    if wheel_filenames:
        logger.info('built wheel for %s', resolved_name)
    return


def _default_build_wheel(ctx, req_type, req, resolved_name, why, sdist_root_dir,
                         build_dependencies):
    build_env = BuildEnvironment(ctx, sdist_root_dir.parent, build_dependencies)
    cmd = [
        'firejail',
        '--net=none',
        build_env.python, '-m', 'pip', '-vvv',
        '--disable-pip-version-check',
        'wheel',
        '--no-cache-dir',
        '--no-build-isolation',
        '--only-binary', ':all:',
        '--wheel-dir', sdist_root_dir.parent.absolute(),
        '--no-deps',
        '.',
    ]
    external_commands.run(cmd, cwd=sdist_root_dir)
    return sdist_root_dir.parent.glob('*.whl')


class BuildEnvironment:
    "Wrapper for a virtualenv used for build isolation."

    def __init__(self, ctx, parent_dir, build_requirements):
        self._ctx = ctx
        self._path = parent_dir / f'build-{platform.python_version()}'
        self._build_requirements = build_requirements
        self._createenv()

    @property
    def python(self):
        return (self._path / 'bin/python3').absolute()

    def _createenv(self):
        self._builder = venv.EnvBuilder(
            clear=True,                 # remove a venv created by previous run
            with_pip=True,              # include pip in the venv
            system_site_packages=True,  # find system package dependencies
        )
        self._builder.create(self._path)
        req_filename = self._path / 'requirements.txt'
        # FIXME: Ensure each requirement is pinned to a specific version.
        with open(req_filename, 'w') as f:
            for r in self._build_requirements:
                if not self._ctx.is_system_requirement(r.name):
                    f.write(f'{r}\n')
        external_commands.run(
            [self.python, '-m', 'pip',
             'install',
             '--disable-pip-version-check',
             '--no-cache-dir',
             '--only-binary', ':all:',
             '--index-url', self._ctx.wheel_server_url,
             '-r', req_filename.absolute(),
             ],
            cwd=self._path.parent,
        )
