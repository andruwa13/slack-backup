from django.conf.urls import include, url
from django.contrib import admin
from backupdata.views import home, stats, team, user, channels, channel_detail, channel_message, channel_detail_name
from user_profile.views import slack_oauth_login, slack_oauth_callback , logout_view



urlpatterns = [
    # Examples:
    url(r'^$', home, name='home'),
    url(r'^stats/$', stats, name='stats'),
    url(r'^team/$', team, name='team'),
    url(r'^team/(?P<username>[\w\-]+)/$', user, name='user'),
    url(r'^emoji/', include('emoji.urls')),
    url(r'^channels$', channels, name='channels'),
    url(r'^channels/(?P<channel_id>\d+)/$', channel_detail, name='channels'),
    url(r'^message/(?P<message_id>\d+)/$', channel_message, name='message'),
    url(r'^channels/(?P<channel_name>[\w\-]+)/$', channel_detail_name, name='channels'),
    url(r'^slack-oauth/login$', slack_oauth_login, name='slack_oauth_login'),
    url(r'^accounts/login/$', slack_oauth_login),
    url(r'^slack-oauth/callback$', slack_oauth_callback, name='slack_oauth_callback'),
    url(r'^logout', logout_view, name='logout_view'),
    url(r'^admin/', include(admin.site.urls)),
]
