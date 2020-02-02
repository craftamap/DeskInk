import imaplib
import logging

class MailHandler(object):
    """Docstring for MailHandler. """

    def __init__(self, config):
        self.logger = logging.getLogger("MailHandler")
        self.connections = {}
        self.config = {k:v for (k, v) in config.items() if "mail_" in k}
        for _, mail_config in self.config.items():
            self._register_mail(**mail_config)

    def count_mails(self):
        counter = 0
        for _, account in self.connections.items():
            account.select("INBOX")
            result_raw = account.search(None, "UNSEEN")
            results = [int(x) for x in result_raw[1][0].decode().split() if x.isnumeric()]
            counter += len(results)
        return counter            

    def _register_mail(self, host, port, username, password):
        try:
            self.logger.info("Registering "+host+"...")
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            self.connections[f"{host}_{username}"] = mail
            self.logger.info("   done!")
        except Exception:
            print("Couldn't connect!")
