#!/usr/bin/env python
import os
import sys

from envs import detect_environment_module


if __name__ == '__main__':
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        detect_environment_module()
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
