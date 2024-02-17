#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# author: Michal Sykora
# server for one application


##############################
### global imports
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import List, Any, Union

##############################
### utils imports
from msy import _LOGGER, clearLoggerHandlers, getLoggingFileName, getDefaultFormater
from msy.asynclogging import AsyncTCPLoggerServer
from msy.utils import NamedClass
from msy.mqtt.logging import RemoteLoggingSettings


#------------------------------------------------------------------------------------------
class RemoteLoggingServer(NamedClass):
	"""
	Server for remote logging of one application
	Handle settings from MQTT and start/stop the actual server
	Contains AsyncTCPLoggerServer for handling the actual logging
	"""
	def __init__(self, name:str):
		super().__init__(name)
		self.__conf = RemoteLoggingSettings()
		self.__logger = self.__createLogger()
		self.__handler = self.__createHandler()
		self.__logger.addHandler(self.__handler)
		self.__server = AsyncTCPLoggerServer(self.__conf.port, self.__logger)

	def setEnabled(self, value:bool) -> None:
		if value != self.__conf.enabled:
			self.__conf.enabled = value
			if self.__conf.enabled:
				self.startServerIfPossible()
			else:
				self.stopServer()

	def setHost(self, value:str) -> None:
		self.__conf.host = value

	def setPort(self, value:int) -> None:
		if value != self.__conf.port:
			_LOGGER.info(f"<{self.name}> - got new port<{value}>, old port<{self.__conf.port}>")
			self.__conf.port = value
			self.__server.port = value
			self.stopServer()
			self.startServerIfPossible()

	def setLevel(self, value:int) -> None:
		self.__conf.level = value

	def setMaxBytes(self, value:int) -> None:
		self.__conf.maxBytes = value
		self.__handler.maxBytes = value

	def setBackupCount(self, value:int) -> None:
		self.__conf.backupCount = value
		self.__handler.backupCount = value

	def isConfigurationValidForServer(self) -> bool:
		# only port is important the rest can be specified durring server running
		return self.__conf.port > 0

	def startServerIfPossible(self) -> None:
		if self.__server.isRunning():
			_LOGGER.debug(f"<{self.name}> - server already running on port<{self.__conf.port}>, don't start it again")
			return
		if not self.__conf.enabled:
			_LOGGER.debug(f"<{self.name}> - not enabled by configuration, don't start server")
			return
		if not self.isConfigurationValidForServer():
			_LOGGER.info(f"<{self.name}> - configuration not valid, cannot start server on port<{self.__conf.port}>")
			return
		_LOGGER.info(f"<{self.name}> - starting server on port<{self.__conf.port}>")
		self.__server.start()

	def stopServer(self) -> None:
		if self.__server.isRunning():
			_LOGGER.info(f"<{self.name}> - stopping server")
			self.__server.stop()

	def __createLogger(self) -> logging.Logger:
		logger = logging.getLogger("remote." + self.name)
		logger.propagate = False
		logger.setLevel(logging.DEBUG)
		clearLoggerHandlers(logger)
		return logger

	def __createHandler(self) -> RotatingFileHandler:
		handler = RotatingFileHandler(filename=getLoggingFileName(self.name), maxBytes=self.__conf.maxBytes, backupCount=self.__conf.backupCount)
		handler.setLevel(logging.DEBUG)
		handler.setFormatter(getDefaultFormater())
		return handler
