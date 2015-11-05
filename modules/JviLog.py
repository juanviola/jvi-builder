import logging

class JviLog:
    def __init__(self, logfilename=None):
        self.logfile = logfilename

    def Log(self, msg, msg_type = None):
        try:
            FORMAT = "%(asctime)-15s %(levelname)s: %(message)s"
            logging.basicConfig(filename=self.logfile, format=FORMAT)
        except IOError, err:
            print err
            print self.logfile

        if msg_type==None or msg_type.lower()=="info":
            logging.getLogger().setLevel(logging.INFO)
            logging.info(msg)
        elif msg_type.lower() in ['warn','error','err','critical','debug']:
            msg_type = msg_type.lower()
        if msg_type=="warn" or msg_type=="warning":
            logging.getLogger().setLevel(logging.WARNING)
            logging.warning(msg)
        elif msg_type=="error" or msg_type=="err":
            logging.getLogger().setLevel(logging.ERROR)
            logging.error(msg)
        elif msg_type=="critical":
            logging.critical(msg)
        elif msg_type=="debug":
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug(msg)

