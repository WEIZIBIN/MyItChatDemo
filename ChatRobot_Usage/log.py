import logging


class LogSystem(object):
    handlerList = []
    showOnCmd = True
    loggingLevel = logging.INFO
    loggingFile = None

    def __init__(self):
        self.logger = logging.getLogger('MyItChatDemo')
        self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(self.loggingLevel)
        self.cmdHandler = logging.StreamHandler()
        self.fileHandler = None
        self.logger.addHandler(self.cmdHandler)

    def set_logging(self, showOnCmd=True, loggingFile=None,
            loggingLevel=logging.INFO,
            formmater=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')):
        if showOnCmd != self.showOnCmd:
            if showOnCmd:
                self.logger.addHandler(self.cmdHandler)
            else:
                self.logger.removeHandler(self.cmdHandler)
            self.showOnCmd = showOnCmd
        if loggingFile != self.loggingFile:
            if self.loggingFile is not None:  # clear old fileHandler
                self.logger.removeHandler(self.fileHandler)
                self.fileHandler.close()
            if loggingFile is not None:  # add new fileHandler
                self.fileHandler = logging.FileHandler(loggingFile)
                self.logger.addHandler(self.fileHandler)
            self.loggingFile = loggingFile
        if loggingLevel != self.loggingLevel:
            self.logger.setLevel(loggingLevel)
            self.loggingLevel = loggingLevel
        for handler in self.logger.handlers:
            if isinstance(handler,logging.Handler):
                handler.setFormatter(formmater)

ls = LogSystem()
set_logging = ls.set_logging
