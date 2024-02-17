#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# author: Michal Sykora
# launch point of application
# It requires aiomqtt library (pip[3] install aiomqtt)
# It requires https://github.com/sajgon11/python-libs installed


##############################
### global imports
import logging

##############################
### utils imports
from msy import initLocalFileLogger, _LOGGER, initDumpLogger
from msy.argparse import initParser, getParser, parseArguments
from msy.asyncio import _GLOBAL_LOOP
from msy.scheduler import _SCHEDULER
from msy.test import initLogger, getMQTTAppName, getMQTTUser, getMQTTPassword
from msy.utils import getLocalHostName, getLocalPrimaryIP
from msy.mqtt.utils import getRetainedMessages, cleanRetainedMessages, dumpMessages

##############################
### local imports
from rlogging import RemoteLogging


#------------------------------------------------------------------------------------------
def getAppName() -> str:
	return getMQTTAppName("rlogging")


#------------------------------------------------------------------------------------------
def getUser() -> str:
	return getMQTTUser("rlogging")


#------------------------------------------------------------------------------------------
def getPassword() -> str:
	return getMQTTPassword("AaUVUaIQcZlWJY1zeYYQL5Ua5iG3GriL")


#------------------------------------------------------------------------------------------
def dumpUsedTopics() -> None:
	initDumpLogger(logging.CRITICAL) # use critical to suppress all other messages
	rLog = RemoteLogging(getAppName(), getUser(), getPassword())
	rLog.dumpTopics(logging.CRITICAL)


#------------------------------------------------------------------------------------------
def dumpRetainTopics() -> None:
	initDumpLogger(logging.CRITICAL) # use critical to suppress all other messages
	dumpMessages(getRetainedMessages(getUser(), getPassword()), logging.CRITICAL)


#------------------------------------------------------------------------------------------
def dumpAndClearRetainTopics() -> None:
	initDumpLogger(logging.CRITICAL) # use critical to suppress all other messages
	dumpMessages(cleanRetainedMessages(getUser(), getPassword()), logging.CRITICAL)


#------------------------------------------------------------------------------------------
def runProgram(useIp:bool) -> None:
	# init test logger or file logger based on testing parameter
	initLogger(initLocalFileLogger, logging.INFO, "rlogging")

	_LOGGER.info("==================================================================")
	_LOGGER.info("============ New run")
	_LOGGER.info("==================================================================")
	_LOGGER.debug("Starting application rlogging")
	hostName = ""
	if useIp:
		hostName = getLocalPrimaryIP()
	else:
		hostName = getLocalHostName()
	rLog = RemoteLogging(getAppName(), getUser(), getPassword(), hostName)
	rLog.start()
	_GLOBAL_LOOP.run_until_complete(_SCHEDULER.run())
	_LOGGER.debug("Done, stopping application rlogging")


#------------------------------------------------------------------------------------------
if __name__ == "__main__":
	initParser("rlogging", "rlogging [action] [testing arguments]",
			 	"""
				Program for remote logging server.
				Logging is done into local files using records transmitted over network from different applications
				Program is listening for remote_trace topics in MQTT and enable/disable servers based on MQTT settings
				""")
	getParser().add_argument("--topic", action="store_true", help="Print used MQTT topics")
	getParser().add_argument("--list", action="store_true", help="Print all MQTT retained message topics as time or test user")
	getParser().add_argument("--clean", action="store_true", help="Print and clean all retained MQTT topics as time or test user")
	getParser().add_argument("--ip", action="store_true", help="Use IP instead of hostname")
	args = parseArguments()

	# check what should I do
	if args.topic:
		dumpUsedTopics()
	elif args.list:
		dumpRetainTopics()
	elif args.clean:
		dumpAndClearRetainTopics()
	else:
		runProgram(args.ip)



