#! /usr/bin/python2

import sys
import tempfile
import logging
import logging.config
import shutil
import string
import threading
import argparse
import datetime
import os.path
import glob
import tarfile
import re
import sh
import blessings
import humanize

#sh.logging_enabled = True

releases = [os.path.basename(folder) for folder in glob.glob('resources/releases/*')]

parser = argparse.ArgumentParser(description='Docker image building tool')
parser.add_argument('-r', '--release', action='store', required=True, choices=releases)
parser.add_argument('-a', '--arch', action='store', required=True, choices=('i386', 'x86_64'))
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('-q', '--quiet', action='store_true', help='Run quietly')
parser.add_argument('-t', '--tar-archive', action='store', help='Target archive file name')
parser.add_argument('-f', '--force', action='store_true', help='Allow existing path as root path')
parser.add_argument('-di', '--docker-import', action='store', help='Store as a docker image')
parser.add_argument('root')

args = parser.parse_args()

def du(path):
    size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            f = os.path.join(root, f)
            if os.path.isfile(f):
                try:
                    fsize = os.path.getsize(os.path.join(root, f))
                    size = size + fsize
                except Exception, e:
                    logger.warn('Error determining %s size' % f, exc_info=True)
    return size
            

level = logging.INFO
if args.verbose:
    level = logging.DEBUG
elif args.quiet:
    level = logging.ERROR

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'stream': sys.stdout
        }
    },
    'root': {
        'handlers': ['console'],
        'level': level,
    }
})
logger = logging.getLogger('main')

if os.path.lexists(args.root):
    if os.path.isdir(args.root):
        if not args.force:
            logger.error('Path %s already exists. Use -f option to force execution. Aborted.' % (args.root, ))
            exit(1)
        else:
            logger.info('Using already created path %s' % (args.root, ))
    else:
        logger.error('%s already exists and is not a path. Aborted.' % (args.root, ))
else:
    os.makedirs(args.root)

archive = args.tar_archive
if archive is None:
    if os.path.basename(args.root) == '':
        logger.error('Empty archive file name ; archive will not be created.')
    else:
        archive_candidate = os.path.basename(args.root) + '.tar.bz2'
        if os.path.lexists(archive_candidate):
            logger.warn('Archive %s already exists. archive will not be created.' % (archive_candidate, ))
        else:
            archive = archive_candidate
            logger.info('Using %s as target archive' % (archive_candidate, ))

tar_flag = None
if archive is not None:
    if os.path.lexists(archive):
        logger.warn('Archive %s already exists. archive will not be created.' % (archive, ))
        archive = None
    if archive.endswith('.tar'):
        tar_flag = ''
    elif archive.endswith('.tar.gz'):
        tar_flag = ':gz'
    elif archive.endswith('.tar.bz2'):
        tar_flag = ':bz2'

releasever = re.findall(r'[0-9]+', args.release)[0]
if args.arch == 'i386':
    arch_wrapper = sh.linux32
else:
    arch_wrapper = sh.linux64

class Processor(object):
    STATE_START = 1
    STATE_PROGRESS = 2
    STATE_LOG = 3
    CONTROL_CHARS_TRANS = dict.fromkeys(range(32))
    PROGRESS = ('-', '\\', '|', '/', '-', '\\', '|', '/')

    def __init__(self, logger, out_level, err_level):
        self.logger = logger
        self.out_level = out_level
        self.err_level = err_level
        self.state = Processor.STATE_START
        self.lock = threading.Lock()
        self.terminal = blessings.Terminal()
        self.progress = 0
        self.width = self.terminal.width - 1

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        sys.stdout.write(self.terminal.clear_eol)
        sys.stdout.write('\r')

    def _log(self, level, line):
        with self.lock:
            sys.stdout.write(self.terminal.clear_eol)
            self.logger.log(level, line.translate(Processor.CONTROL_CHARS_TRANS))
            self.state = Processor.STATE_LOG

    def _progress(self, line):
        self.progress = self.progress + 1
        offset = self.progress % 8
        with self.lock:
            sys.stdout.write(self.terminal.clear_eol)
            sys.stdout.write('[')
            sys.stdout.write(Processor.PROGRESS[offset])
            sys.stdout.write('] ')
            sys.stdout.write(line.translate(Processor.CONTROL_CHARS_TRANS))
            sys.stdout.write('\r')
            sys.stdout.flush()
            self.state = Processor.STATE_PROGRESS

    def _callback(self, level):
        def callback(line):
            if self.logger.isEnabledFor(level):
                self._log(level, line)
            else:
                self._progress(line)
        return callback

    def stdout(self):
        return self._callback(self.out_level)

    def stderr(self):
        return self._callback(self.err_level)

class shelper(object):
    def __init__(self):
        self._chroot = None
        self._processor = None
        self._arch = None

    def chroot(self, chroot):
        self._chroot = chroot
        return self

    def processor(self, processor):
        self._processor = processor
        return self

    def arch(self, arch):
        self._arch = arch
        return self

    def run(self, command, *args, **kwargs):
        args = list(args)
        kwargs = dict(**kwargs)
        cmd = command
        if self._chroot is not None:
            args.insert(0, cmd._path)
            args.insert(0, self._chroot)
            cmd = sh.chroot
        if self._arch is not None:
            args.insert(0, cmd._path)
            cmd = self._arch
        if self._processor is not None:
            kwargs['_out'] = self._processor.stdout()
            kwargs['_err'] = self._processor.stderr()
            kwargs['_tty_out'] = False
        kwargs['_decode_errors'] = 'replace'
        if self._processor is not None:
            with self._processor:
                result = cmd(*args, **kwargs).wait()
        else:
            result = cmd(*args, **kwargs)
        return result

# python-sh checks command before to run it
# it can be problematic for chrooted commands
# full path is also a must, as path resolution
# can be erroneous in chroot environment
def fake_command(cmd):
    command = sh.Command('/bin/true')
    command._path = cmd
    return command

yum = fake_command('/usr/bin/yum')
locale = fake_command('/root/locale.sh')
rpm = fake_command('/bin/rpm')

# for execution timing
start_time = datetime.datetime.now()

# configuration choosen by release
yum_repos_d = tempfile.mkdtemp(prefix = 'yum_repos_d_')
yum_conf = tempfile.mkstemp(prefix = 'yum_conf_')[1]

logger.info('Using temporary configuration %s - %s' %
	(yum_repos_d, yum_conf))

shutil.copyfile('resources/releases/%s/yum.conf' % (args.release, ), yum_conf)
with open(yum_conf, 'a') as f:
	f.write('reposdir=%s' % (yum_repos_d, ))

sh.cp('-ar', sh.glob('resources/releases/%s/yum.repos.d/*' % (args.release, )), yum_repos_d)

rpm_dir = '%s/etc/rpm' % (args.root, )
logger.info('Copying rpm configuration in %s' % (rpm_dir, ))
shelper().run(sh.mkdir, '-p', rpm_dir)
shutil.copy('resources/macros.langs', rpm_dir)

try:
    with open('resources/packages') as package_file:
        package_list = [line.replace('\n', '') for line in package_file]
except:
    logger.error('Error reading package list')
    sys.exit(1)

logger.info('Installing packages %s' % (', '.join(package_list), ))
processor = Processor(logger, logging.DEBUG, logging.WARN)
shelper().arch(arch_wrapper).processor(processor).run(
        yum,
        '-y', '--releasever=%s' % (releasever, ),
        '-c', yum_conf,
        '--installroot=%s' % (args.root, ),
        '--nogpgcheck',
        'install',
        *package_list
)
logger.info('Installing packages done')

shelper().processor(processor).chroot(args.root).run(sh.rm, '-rf', '/var/lib/rpm/__db*', '/var/lib/rpm/Name')
shelper().processor(processor).chroot(args.root).run(rpm, '--rebuilddb')

shutil.copy('resources/locale.sh', '%s/root/' % (args.root, ))

logger.info('Cleaning')
shelper().arch(arch_wrapper).processor(processor).chroot(args.root).run(yum, 'history', 'new')
shelper().arch(arch_wrapper).processor(processor).chroot(args.root).run(yum, 'clean', 'all')
shelper().arch(arch_wrapper).processor(processor).chroot(args.root).run(locale)
logger.info('Cleaning done')

shutil.copy('/etc/resolv.conf', '%s/etc/' % (args.root, ))
shelper().arch(arch_wrapper).processor(processor).chroot(args.root).run(rpm, '-qa')

image_size = du(args.root)
logger.info('Image size : %s' % humanize.naturalsize(image_size))
last_step_time = datetime.datetime.now()
installation_ellapsed_time = last_step_time - start_time
logger.info('Installation elapsed time %s' % (installation_ellapsed_time, ))

if archive is not None:
    with tarfile.open(archive, 'w' + tar_flag) as archive_tar:
        archive_tar.add(args.root, '/')
    tar_ellapsed_time = datetime.datetime.now() - last_step_time
    last_step_time = datetime.datetime.now()
    logger.info('Archive elapsed time %s' % (tar_ellapsed_time, ))
    logger.info('Archive size : %s' % humanize.naturalsize(os.path.getsize(archive)))

    if args.docker_import is not None:
        with open(archive, 'r') as archivef:
            shelper().processor(processor).run(sh.docker, 'import', '-', args.docker_import, _in=archivef, _in_bufsize=10000000)
