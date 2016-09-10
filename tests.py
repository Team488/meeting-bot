import os

from errbot.backends.test import testbot

class TestAreWeMeeting(object):
    extra_plugin_dir = '.'

    def test_ask_if_coming(self, testbot):
        testbot.push_message('!ask_if_coming Sept-15')
        assert 'Would you come to a meeting on' in testbot.pop_message()
        assert 'Members asked' in testbot.pop_message()

    def test_make_call_with_no_meeting(self, testbot):
        testbot.push_message('!make_call')
        assert "No current meeting proposed." in testbot.pop_message()

    def test_yes(self, testbot):
        testbot.push_message('!ask_if_coming Sept-15')
        assert 'Would you come to a meeting on' in testbot.pop_message()
        assert 'Members asked' in testbot.pop_message()
        testbot.push_message('!yes')

