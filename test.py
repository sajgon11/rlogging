#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# author: Michal Sykora
# testing client for rlogging
# It requires aiomqtt library (pip[3] install aiomqtt)
# It requires https://github.com/sajgon11/python-libs installed


##############################
### global imports
import logging
import random

##############################
### utils imports
from msy import initTestLogger, _LOGGER
from msy.argparse import initParser, getParser, parseArguments
from msy.asyncio import _GLOBAL_LOOP
from msy.mqtt import AppMQTTConnection
from msy.scheduler import _SCHEDULER
from msy.utils import getLocalHostName


#------------------------------------------------------------------------------------------
def remoteLog() -> None:
	number = random.randint(1, 54354345)
	_LOGGER.debug(f"Debug message<{number}>")
	_LOGGER.info(f"Debug message<{number}>")
	_LOGGER.warning(f"Debug message<{number}>")
	_LOGGER.error(f"Debug message<{number}>")
	try:
		raise ValueError(f"Failed with message<{number}>")
	except ValueError:
		_LOGGER.exception(f"Got exception message<{number}>")


#------------------------------------------------------------------------------------------
def runProgram(appName:str, port:int) -> None:
	initTestLogger()

	_LOGGER.info("==================================================================")
	_LOGGER.debug("Starting application test")
	connection = AppMQTTConnection(appName, "shsystem", "o53kf6Z76ws6VenKAEdtVc1kNcpSKvDv")  # user shsystem can write to all param and _param topics...
	connection.addRemoteLogging(True, logging.DEBUG, port, host=getLocalHostName())
	connection.start()

	random.seed()

	_SCHEDULER.scheduleRepeating(10, remoteLog)

	_GLOBAL_LOOP.run_until_complete(_SCHEDULER.run())
	_LOGGER.debug("Done, stopping application rlogging")


#------------------------------------------------------------------------------------------
if __name__ == "__main__":
	initParser("test", "test appName port",
			 	"""
				Program for remote logging server.
				Logging is done into local files using records transmitted over network from different applications
				Program is listening for remote_trace topics in MQTT and enable/disable servers based on MQTT settings
				""")
	getParser().add_argument("appName", help="Application name used for MQTT")
	getParser().add_argument("port", type=int help="Initial port for remote logging")
	args = parseArguments()

	runProgram(args.appName, args.port)



