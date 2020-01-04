#! /bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function

import logging

import click

import clickable.utils
import clickable.coloredlogs

import clickable_ansible


# bootstrap logging system
clickable.coloredlogs.bootstrap()
logger = logging.getLogger('stdout.clickable')


# name consistently with pyproject.toml entrypoint
@click.group()
@click.pass_context
def main(ctx):
    """
    Deployment or development tasks
    """
    clickable.utils.load_config(ctx, __name__, __file__, 'clickables.yml')


clickable_ansible.run_playbook_task(main, 'steam', 'playbooks/steam.yml',
        common_hosts='localhost',
        help='Install Steam')
clickable_ansible.run_playbook_task(main, 'minecraft', 'playbooks/minecraft.yml',
        common_hosts='localhost',
        help='Install Minecraft')
