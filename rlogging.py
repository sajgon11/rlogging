#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# author: Michal Sykora
# module for remote logging


##############################
### global imports
import logging
from typing import Dict

##############################
### utils imports
from msy import _LOGGER
from msy.mqtt import AppMQTTConnection
from msy.scheduler import _SCHEDULER
from msy.utils import getLocalHostName
from msy.mqtt.helper import buildTrigger
from msy.mqtt.logging import RemoteLoggingSettings, TOPIC_REMOTE_ENABLED, TOPIC_REMOTE_HOST, TOPIC_REMOTE_PORT, TOPIC_REMOTE_LEVEL, TOPIC_REMOTE_MAXBYTES, TOPIC_REMOTE_BACKUPCOUNT
from msy.mqtt.topic import AppTopicBuilder

##############################
### local imports
from server import RemoteLoggingServer


PERIODIC_DUMP_INTERVAL = 900 # periodic dump every 15 minutes


#------------------------------------------------------------------------------------------
class RemoteLogging(object):
	def __init__(self, appName:str, userName:str, password:str) -> None:
		self.__connect = AppMQTTConnection(appName, userName, password)
		self.__servers:Dict[str, RemoteLoggingServer] = {}
		self.__localHostName = getLocalHostName()
		#
		self.__initMQTT()

	def dump(self, level:int) -> None:
		_LOGGER.log(level,  "==================================================================")
		_LOGGER.log(level,  "============ Periodic dump")
		_LOGGER.log(level, f"Still running and listenning on host<{self.__localHostName}>")
		for server in self.__servers.values():
			server.dump(level)
		_LOGGER.log(level,  "==================================================================")

	def dumpTopics(self, level:int) -> None:
		self.__connect.dumpTopics(level)

	def start(self) -> None:
		self.__connect.start()
		_SCHEDULER.scheduleRepeating(PERIODIC_DUMP_INTERVAL, self.__periodicDump)

	def stop(self) -> None:
		self.__connect.stop()
		_SCHEDULER.cancelAllByCallback(self.__periodicDump)

	def __onEnabledChanged(self, topic:str, value:bool) -> None:
		_LOGGER.debug(f"Got new enabled<{value}> from topic<{topic}")
		name = self.__getAppNameFromTopic(topic)
		server = self.__getOrCreateServer(name)
		server.setEnabled(value)

	def __onHostChanged(self, topic:str, value:str) -> None:
		_LOGGER.debug(f"Got new host<{value}> from topic<{topic}")
		name = self.__getAppNameFromTopic(topic)
		server = self.__getOrCreateServer(name)
		server.setHost(value)

	def __onPortChanged(self, topic:str, value:int) -> None:
		_LOGGER.debug(f"Got new port<{value}> from topic<{topic}")
		name = self.__getAppNameFromTopic(topic)
		server = self.__getOrCreateServer(name)
		server.setPort(value)

	def __onLevelChanged(self, topic:str, value:int) -> None:
		_LOGGER.debug(f"Got new level<{value}> from topic<{topic}")
		name = self.__getAppNameFromTopic(topic)
		server = self.__getOrCreateServer(name)
		server.setLevel(value)

	def __onMaxBytesChanged(self, topic:str, value:int) -> None:
		_LOGGER.debug(f"Got new max bytes<{value}> from topic<{topic}")
		name = self.__getAppNameFromTopic(topic)
		server = self.__getOrCreateServer(name)
		server.setMaxBytes(value)

	def __onBackupCountChanged(self, topic:str, value:int) -> None:
		_LOGGER.debug(f"Got new backup count<{value}> from topic<{topic}")
		name = self.__getAppNameFromTopic(topic)
		server = self.__getOrCreateServer(name)
		server.setBackupCount(value)

	def __initMQTT(self) -> None:
		conf = RemoteLoggingSettings()
		builder = AppTopicBuilder("+")
		self.__connect.addSubscribe(buildTrigger(builder.buildInternalParameterGetTopic(TOPIC_REMOTE_ENABLED), self.__onEnabledChanged, type(conf.enabled), includeTopicInCallback=True))
		self.__connect.addSubscribe(buildTrigger(builder.buildInternalParameterGetTopic(TOPIC_REMOTE_HOST), self.__onHostChanged, type(conf.host), includeTopicInCallback=True))
		self.__connect.addSubscribe(buildTrigger(builder.buildInternalParameterGetTopic(TOPIC_REMOTE_PORT), self.__onPortChanged, type(conf.port), includeTopicInCallback=True))
		self.__connect.addSubscribe(buildTrigger(builder.buildInternalParameterGetTopic(TOPIC_REMOTE_LEVEL), self.__onLevelChanged, type(conf.level), includeTopicInCallback=True))
		self.__connect.addSubscribe(buildTrigger(builder.buildInternalParameterGetTopic(TOPIC_REMOTE_MAXBYTES), self.__onMaxBytesChanged, type(conf.maxBytes), includeTopicInCallback=True))
		self.__connect.addSubscribe(buildTrigger(builder.buildInternalParameterGetTopic(TOPIC_REMOTE_BACKUPCOUNT), self.__onBackupCountChanged, type(conf.backupCount), includeTopicInCallback=True))

	def __getAppNameFromTopic(self, topic:str) -> str:
		appName = topic.split("/")[0]
		return appName

	def __getOrCreateServer(self, name:str) -> RemoteLoggingServer:
		if not name in self.__servers:
			_LOGGER.info(f"Creating new server<{name}>")
			self.__servers[name] = RemoteLoggingServer(name, self.__localHostName)
		return self.__servers[name]

	def __periodicDump(self) -> None:
		self.dump(logging.INFO)
