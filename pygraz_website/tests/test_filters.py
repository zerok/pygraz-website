import collections
from pygraz_website import filters

class TestFilters(object):
    def test_url_detection(self):
        """
        Test that urls are found correctly.
        """
        no_urls_string = '''This is a test without any urls in it.'''
        urls_string = '''This string has one link in it: http://pygraz.org . But it also has some text after it :D'''
        assert filters.urlize(no_urls_string) == no_urls_string
        assert filters.urlize(urls_string) == '''This string has one link in it: <a href="http://pygraz.org">http://pygraz.org</a> . But it also has some text after it :D'''
        assert filters.urlize(urls_string, True).matches == {'urls': set(['http://pygraz.org'])}
        assert filters.urlize(None) == u''
        assert filters.urlize("'http://test.com'") == """'<a href="http://test.com">http://test.com</a>'"""

    def test_namehandles(self):
        """
        Tests the discory of linkable names.
        """
        string_with_handles = 'Hallo @pygraz.'
        assert filters.urlize(string_with_handles) == 'Hallo <a href="http://twitter.com/pygraz">@pygraz</a>.'
        assert filters.urlize(string_with_handles, True).matches == {'handles': set(['pygraz'])}

    def test_hashtags(self):
        string_with_tags = 'This is a #test for #hashtags'
        assert filters.urlize(string_with_tags) == 'This is a <a href="http://twitter.com/search?q=%23test">#test</a> for <a href="http://twitter.com/search?q=%23hashtags">#hashtags</a>'
        assert filters.urlize(string_with_tags, True).matches == {'hashtags': set(['test', 'hashtags'])}
