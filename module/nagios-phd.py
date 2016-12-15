#!/usr/bin/env python
# coding: utf8

from __future__ import unicode_literals

import begin
import json
import logging
import boto3

# Time to debug...
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def _init_aws_session(boto_profile='int'):
    # Let's go
    try:
        session = boto3.Session(profile_name=boto_profile)
    except ProfileNotFound as e:
        logger.error(e)
        raise SystemExit, 1

    return session


@begin.start
@begin.logging
def run(Version, timeout, warning, critical,
	username="int", Hostname='eu-west-1', ):

	logger.debug("+ C'est parti")

	# Switch parsing https://nagios-plugins.org/doc/guidelines.html#PLUGOUTPUT
	'''
	There are a few reserved options that should not be used for other purposes:

          -V version (--version)
          -h help (--help)
          -t timeout (--timeout)
          -w warning threshold (--warning)
          -c critical threshold (--critical)
          -H hostname (--hostname)
          -v verbose (--verbose)
	In addition to the reserved options above, some other standard options are:

          -C SNMP community (--community) => useless
          -a authentication password (--authentication) => useless
          -l login name (--logname) => useless
          -p port or password (--port or --passwd/--password)monitors operational => useless
          -u url or username (--url or --username)
	'''

	logger.debug( "+ Connecting to %s" % username)
	session = _init_aws_session(username)
	client = session.client('health')

	filters = {
		'eventArns': ['arn:aws:health:us-east-1::event/AWS_EC2_MAINTENANCE_5331'],
	}
	response = client.describe_affected_entities(filter=filters)
