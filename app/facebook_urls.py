#!/usr/bin/python

fb_urls = [
    'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=907786629329598&client_secret=a8e07a882c00c5b07afa789d1ab915bf&fb_exchange_token=EAAM5oIuSsr4BAOcwohHylhwcM9WQ8gGaiEhjEX7wJo3nqiQeadp1BNuwifZCXhHQlCCm7nipZAG8oQ1P7nEIMkOZAHi9BdkOX0Mi32IqBiK8j8m73YBRbcwncTTsvQeRu6gHDt4zEMgcZANzbMceQVRxTbExvTgmsJ1ZAGNn2XTQrzOiL61G9',
    'https://graph.facebook.com/v2.4/me?access_token=EAAM5oIuSsr4BAF4PpQ6InmrghTMdwZAm4db9gXuORq2rKQSfZAcYFlq12GdJnPOuwcqldk4NiEVKPIgFpGpIosdDMh1bZBpkCtwLjCTZBP9ZBEaJhUcpHz9L2mD5LwMGecpiXxpF7UzL3WOuLElKjVtbSeqnrZAV8ZD&fields=name,id,email',
    'https://graph.facebook.com/v2.4/me/picture?access_token=EAAM5oIuSsr4BAF4PpQ6InmrghTMdwZAm4db9gXuORq2rKQSfZAcYFlq12GdJnPOuwcqldk4NiEVKPIgFpGpIosdDMh1bZBpkCtwLjCTZBP9ZBEaJhUcpHz9L2mD5LwMGecpiXxpF7UzL3WOuLElKjVtbSeqnrZAV8ZD&redirect=0&height=200&width=200'
]

user_data = {u'email': u'al.carruth@gmail.com', u'name': u'Al Carruth', u'id': u'10154076807928706'}
