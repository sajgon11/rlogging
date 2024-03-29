#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# author: Michal Sykora
# server for one application


##############################
### global imports
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

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
	def __init__(self, name:str, localHostName:str):
		super().__init__(name)
		self.__conf = RemoteLoggingSettings()
		self.__logger = self.__createLogger()
		self.__handler:Optional[RotatingFileHandler] = None
		self.__server = AsyncTCPLoggerServer(self.__conf.port, self.__logger)
		self.__localHostName = localHostName

	def dump(self, level:int) -> None:
		_LOGGER.log(level,  "------------------------------------------------------------------")
		_LOGGER.log(level, f"Server<{self.name}>")
		_LOGGER.log(level, f"Configuration<{self.__conf}>")
		_LOGGER.log(level, f"Runnig<{self.__server.isRunning()}>, connected clients<{self.__server.getCountOfClients()}>")
		_LOGGER.log(level,  "------------------------------------------------------------------")

	def setEnabled(self, value:bool) -> None:
		if value != self.__conf.enabled:
			self.__conf.enabled = value
			if self.__conf.enabled:
				self.startServerIfPossible()
			else:
				self.stopServer()

	def setHost(self, value:str) -> None:
		if value != self.__conf.host:
			_LOGGER.info(f"<{self.name}> - got new host<{value}>, old host<{self.__conf.host}>")
			self.__conf.host = value
			# host was changed
			# check if host is my local host name
			# server should be running only for local server
			self.stopServer()
			self.startServerIfPossible()

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
		if self.__handler is not None:
			self.__handler.maxBytes = value

	def setBackupCount(self, value:int) -> None:
		self.__conf.backupCount = value
		if self.__handler is not None:
			self.__handler.backupCount = value

	def isConfigurationValidForServer(self) -> bool:
		# only port is important - we need to listen on
		# valid configuration have the correct host
		return self.__conf.port > 0 and self.__conf.host == self.__localHostName

	def startServerIfPossible(self) -> None:
		if self.__server.isRunning():
			_LOGGER.debug(f"<{self.name}> - server already running on<{self.__conf.host}:{self.__conf.port}>, don't start it again")
			return
		if not self.__conf.enabled:
			_LOGGER.debug(f"<{self.name}> - not enabled by configuration, don't start server on<{self.__conf.host}:{self.__conf.port}>")
			return
		if not self.isConfigurationValidForServer():
			_LOGGER.info(f"<{self.name}> - configuration not valid, cannot start server on<{self.__conf.host}:{self.__conf.port}>")
			return
		_LOGGER.info(f"<{self.name}> - starting server on <{self.__conf.host}:{self.__conf.port}>")
		self.__addHandler()
		self.__server.start()

	def stopServer(self) -> None:
		if self.__server.isRunning():
			_LOGGER.info(f"<{self.name}> - stopping server")
			self.__removeHandler()
			self.__server.stop()

	def __createLogger(self) -> logging.Logger:
		logger = logging.getLogger("remote." + self.name)
		logger.propagate = False
		logger.setLevel(logging.DEBUG)
		clearLoggerHandlers(logger)
		return logger

	def __addHandler(self) -> None:
		if self.__handler is None:
			self.__handler = RotatingFileHandler(filename=getLoggingFileName(self.name), maxBytes=self.__conf.maxBytes, backupCount=self.__conf.backupCount)
			self.__handler.setLevel(logging.DEBUG)
			self.__handler.setFormatter(getDefaultFormater())
			self.__logger.addHandler(self.__handler)

	def __removeHandler(self) -> None:
		if self.__handler is not None:
			self.__logger.removeHandler(self.__handler)
			self.__handler = None
