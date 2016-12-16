#!/usr/bin/env python
# coding: utf8

from __future__ import unicode_literals

import begin
import json
import logging
import boto3

NAGIOS_STATUS_OK = 0
NAGIOS_STATUS_WARNING = 1
NAGIOS_STATUS_CRITICAL = 2
NAGIOS_STATUS_UNKNOWN = 3

def _init_aws_session(boto_profile='int'):
    # Let's go
    try:
        session = boto3.Session(profile_name=boto_profile)
    except ProfileNotFound as e:
        logging.error(e)
        raise SystemExit, 1

    return session

def _this_is_the_end(error_code=NAGIOS_STATUS_UNKNOWN, output=u"I know nothing"):
  logging.debug("+ All done, I quit! (with %s)" % error_code)
  print output
  raise SystemExit(error_code)

@begin.start
@begin.logging
def run(warning=1, critical=0, username="int", Hostname='eu-west-1', loglvl='ERROR'):
  "Query AWS Personal Health Dashboard for any open events"

  logging.debug("---------------------------------------------------------")
  logging.debug("+ C'est parti")

  module_output = "Blackhole..."
  module_return_code = NAGIOS_STATUS_UNKNOWN

  logging.debug( "+ Using profile %s" % username)
  session = _init_aws_session(username)
  client = session.client('health', 'us-east-1') # Only entrypoint for now

  filters = {
    'regions': [Hostname],
    'eventStatusCodes': ['open'],
  }
  logging.debug('+ Filters: %s' % filters)

  try:
    '''response = client.describe_event_aggregates(
                  aggregateField = 'eventTypeCategory',
                  filter = filters,
            
                )'''

    response = client.describe_events(
      filter = filters,
    )
  except "AccessDeniedException":
    logging.error('Profile % is not authorized' % username)
    _this_is_the_end(NAGIOS_STATUS_UNKNOWN, "Unable to query AWS Health")

  number_events = len(response['events'])
  logging.debug('+ %s event(s) matched filters' % number_events)

  if number_events == 0:
    logging.debug('+ Pas un probleme')
    _this_is_the_end(NAGIOS_STATUS_OK, "So far so good |0")

  if warning and number_events >= warning:
    module_return_code = NAGIOS_STATUS_WARNING
    logging.debug('+ Warning will be returned as above specified threshold'
     ' of %s' % warning)

  if critical and number_events >= critical:
    module_return_code = NAGIOS_STATUS_CRITICAL
    logging.debug('+ Critical will be returned as above specified threshold'
      ' of %s' % critical)

  module_output = u"%s incident(s) en cours |%s\n" % (number_events, number_events)

  for event in response['events']:
    module_output += u"%s is an %s on %s\n" % (
      event.get("arn"),
      event.get("eventTypeCategory"),
      event.get("service"),
    )

  _this_is_the_end(module_return_code, module_output)
