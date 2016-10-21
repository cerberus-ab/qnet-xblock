# dependencies
import json
import os
import imp

from getpass import getpass
from fabric.colors import *
from fabric.api import *

root_dir = os.path.dirname(__file__)

# using configuration message
if not hasattr(env, 'conf'):
    abort("'conf' param is not set")

print "Using %s configuration" % yellow(env.conf)


# try import config
try:
    env_conf = imp.load_source('env_conf', reduce(os.path.join, [root_dir, 'deploy', env.conf]) + '.py')
    config = env_conf.config
except IOError as e:
    abort("Unable to find %s config\n" % env.conf)

# get env params
env.user = config['username']
env.hosts = [config['host']]
env.port = config['port']

# prompt the password
env.password = getpass("Enter the password for %s@%s: " % (env.user, env.hosts[0]))


def deploy_copy():
    """Deploy xblock to the target machine"""
    # TODO: add flag to remove dest_dir after

    # make clean dest directory
    run('mkdir -p %s' % config['dest_dir'], quiet=True)
    with cd(config['dest_dir']):
        run('rm -rf *', quiet=True)

    # copy project
    put('%s/qnet*' % root_dir, config['dest_dir'])
    put('%s/setup.py' % root_dir, config['dest_dir'])

    # install xblock and restart edx
    run("sudo -u edxapp /edx/bin/pip.edxapp install %s --no-cache-dir ; /edx/bin/supervisorctl restart edxapp:" % config['dest_dir'])

def deploy():
    """Deploy xblock using repository"""
    # install xblock and restart edx
    run("sudo -Hu edxapp /edx/bin/pip.edxapp install -e git+https://github.com/cerberus-ab/qnet-xblock.git#egg=qnet-xblock ; /edx/bin/supervisorctl restart edxapp:")
