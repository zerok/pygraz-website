import postmark
import unittest
import warnings
import logging


logger = logging.getLogger(__name__)


class Postmark(object):
    """
    A simple postmark loader that prefills mail objects with things like the api key.
    """

    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if 'POSTMARK_API_KEY' not in self.app.config:
            warnings.warn("POSTMARK_API_KEY not set in the configuration!")

    def get_config(self, key):
        return self.app.config.get('POSTMARK_{}'.format(key))

    def create_mail(self, *args, **kwargs):
        test_mode = kwargs.get('test_mode', None)
        if test_mode is None:
            test_mode = self.get_config('TEST_MODE')
        if test_mode:
            mail = PMTestMail(*args, **kwargs)
        else:
            mail = postmark.PMMail(*args, **kwargs)
        mail.api_key = self.get_config('API_KEY')
        if 'sender' not in kwargs:
            mail.sender = self.get_config('SENDER')
        return mail

    def send_bcc_batch(self, mail, recipients):
        """
        This method basically sends a batch of mails by setting the
        recipients via the bcc header. It does not touch the bcc 
        header.
        """
        if len(recipients) == 1:
            mail.to = recipients[0]
            mail.send()
            return
        mail.recipient = mail.sender
        for recs in _split_recipients(recipients, max_num=20):
            mail.bcc = ','.join(recs)
            logger.debug("Sending mail to {}".format(mail.bcc))
            mail.send()


class PMTestMail(postmark.PMMail):
    def send(self, *args, **kwargs):
        kwargs['test'] = True
        return super(PMTestMail, self).send(*args, **kwargs)


def _split_recipients(recipients, max_num=20):
    """
    Generates lists of recipients with a maximum of 20.
    """
    result = []
    for i, elem in enumerate(recipients):
        result.append(elem)
        if i % max_num == (max_num - 1):
            yield result
            result = []
    if result:
        yield result


class UtilityTests(unittest.TestCase):
    def testSplitter(self):
        l = range(10)
        last_i = None
        for i, sublist in enumerate(_split_recipients(l, max_num=3)):
            last_i = i
            if i == 0:
                self.assertEqual(3, len(sublist))
                self.assertListEqual([0, 1, 2], sublist)
            elif i == 1:
                self.assertEqual(3, len(sublist))
                self.assertListEqual([3, 4, 5], sublist)
            elif i == 2:
                self.assertEqual(3, len(sublist))
                self.assertListEqual([6, 7, 8], sublist)
            elif i == 3:
                self.assertEqual(1, len(sublist))
                self.assertListEqual([9], sublist)
            else:
                self.fails("Generator didn't stop")
        self.assertEquals(3, last_i)


if __name__ == '__main__':
    unittest.main()
