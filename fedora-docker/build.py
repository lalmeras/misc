#! /usr/bin/python2

import sys
import tempfile
import logging
import logging.config
import shutil
import string
import threading
import argparse
import sh
import blessings

parser = argparse.ArgumentParser(description='Docker image building tool')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-q', '--quiet', action='store_true')
parser.add_argument('root')

args = parser.parse_args()

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
            sys.stdout.write(line.strip().translate(Processor.CONTROL_CHARS_TRANS))
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

yum_repos_d = tempfile.mkdtemp(prefix = 'yum_repos_d_')
yum_conf = tempfile.mkstemp(prefix = 'yum_conf_')[1]

logger.info('Using temporary configuration %s - %s' %
	(yum_repos_d, yum_conf))

shutil.copyfile('resources/yum.conf', yum_conf)
with open(yum_conf, 'a') as f:
	f.write('reposdir=%s' % (yum_repos_d, ))

sh.cp('-ar', sh.glob('resources/yum.repos.d/*'), yum_repos_d)

rpm_dir = '%s/etc/rpm' % (args.root, )
logger.info('Copying rpm configuration in %s' % (rpm_dir, ))
sh.mkdir('-p', rpm_dir)
shutil.copy('resources/macros.langs', rpm_dir)

try:
    with open('resources/packages') as package_file:
        package_list = [line.replace('\n', '') for line in package_file]
except:
    logger.error('Error reading package list')
    sys.exit(1)

logger.info('Installing packages %s' % (', '.join(package_list), ))
processor = Processor(logger, logging.DEBUG, logging.WARN)
with processor:
    print sh.yum(
    	sh.cat('resources/packages'),
    	'-y', '--releasever=21',
    	'-c', yum_conf,
    	'--installroot=%s' % (args.root, ),
    	'install',
        *package_list,
    	_out=processor.stdout(), _err=processor.stderr(),
        _tty_out=False
    )
logger.info('Installing packages done')

shutil.copy('resources/locale.sh', '%s/root' % (args.root, ))

logger.info('Cleaning')
with processor:
    sh.chroot(args.root, '/root/locale.sh',
            _out=processor.stdout(), _err=processor.stderr())
    sh.chroot(args.root, 'yum', 'clean', 'all',
            _out=processor.stdout(), _err=processor.stderr())
logger.info('Cleaning done')

image_size = sh.cut(
        sh.du('-sh', args.root), '-f1')
logger.info('Image size %s' % (image_size, ))
