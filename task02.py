# Task 2 - notifier
#
# 2.1 TelegramNotifier has no method send(), it only has sned(), which is just a new name for python.
#     So it inherits the empty send() from Notifier, notify() calls it and pass does nothing, no error.
# 2.3 send() is abstract because every channel sends in its own way. notify() is concrete
#     because the cutting by max_length is the same for all channels, so it is written once.
#     max_length is just a normal class attribute.

from abc import ABC, abstractmethod
import pytest


class Notifier(ABC):
    max_length = 1000

    @abstractmethod
    def send(self, recipient, text):
        pass

    def notify(self, recipient, text):
        self.send(recipient, text[: self.max_length])


class TelegramNotifier(Notifier):
    max_length = 4096

    def __init__(self):
        self.sent = []

    def send(self, recipient, text):
        self.sent.append((recipient, text))
        print(f"telegram -> {recipient}: {text}")


class SmsNotifier(Notifier):
    max_length = 160

    def __init__(self):
        self.sent = []

    def send(self, recipient, text):
        self.sent.append((recipient, text))
        print(f"sms -> {recipient}: {text}")


def test_notifier_cannot_be_created():
    with pytest.raises(TypeError):
        Notifier()


def test_typo_is_found_when_object_created():
    class BadTelegram(Notifier):
        max_length = 4096

        def sned(self, recipient, text):
            print("never")

    with pytest.raises(TypeError):
        BadTelegram()


def test_telegram_delivers():
    t = TelegramNotifier()
    t.notify("@ali", "Exam at 10:00")
    assert t.sent == [("@ali", "Exam at 10:00")]


def test_each_channel_cuts_to_own_limit():
    text = "a" * 5000
    tg = TelegramNotifier()
    sms = SmsNotifier()
    tg.notify("@ali", text)
    sms.notify("+998901234567", text)
    assert len(tg.sent[0][1]) == 4096
    assert len(sms.sent[0][1]) == 160


def test_short_text_stays_same():
    sms = SmsNotifier()
    sms.notify("+998901234567", "hi")
    assert sms.sent[0][1] == "hi"
