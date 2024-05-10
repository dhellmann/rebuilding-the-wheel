import logging
import os
import shlex
import subprocess

logger = logging.getLogger(__name__)


# based on pyproject_hooks/_impl.py: quiet_subprocess_runner
def run(cmd, cwd=None, extra_environ={}, log_filename=None):
    """Call the subprocess while logging output
    """
    env = os.environ.copy()
    env.update(extra_environ)

    logger.debug(
        'running: %s %s',
        ' '.join('%s=%s' % x for x in extra_environ.items()),
        ' '.join(shlex.quote(str(s)) for s in cmd)
    )
    if log_filename:
        with open(log_filename, 'w') as log_file:
            completed = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        with open(log_filename, 'r', encoding='utf-8') as f:
            output = f.read()
    else:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output = completed.stdout.decode('utf-8') if completed.stdout else ''
    if completed.returncode != 0:
        logger.error('%s failed with %s', cmd, output)
        raise subprocess.CalledProcessError(completed.returncode, cmd, output)
    logger.debug('output: %s', output)
    return output
