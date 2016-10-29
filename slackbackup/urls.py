from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'backupdata.views.home', name='home'),
    url(r'^stats/$', 'backupdata.views.stats', name='stats'),
    url(r'^team/$', 'backupdata.views.team', name='team'),
    url(r'^team/(?P<username>[\w\-]+)/$', 'backupdata.views.user', name='user'),
    url(r'^emoji/', include('emoji.urls')),
    url(r'^channels$', 'backupdata.views.channels', name='channels'),
    url(r'^channels/(?P<channel_id>\d+)/$', 'backupdata.views.channel_detail', name='channels'),
    url(r'^message/(?P<message_id>\d+)/$', 'backupdata.views.channel_message', name='message'),
    url(r'^channels/(?P<channel_name>[\w\-]+)/$', 'backupdata.views.channel_detail_name', name='channels'),
    url(r'^slack-oauth/login$', 'user_profile.views.slack_oauth_login', name='slack_oauth_login'),
    url(r'^accounts/login/$', 'user_profile.views.slack_oauth_login'),
    url(r'^slack-oauth/callback$', 'user_profile.views.slack_oauth_callback', name='slack_oauth_callback'),
    url(r'^logout', 'user_profile.views.logout_view', name='logout_view'),
    url(r'^admin/', include(admin.site.urls)),
)
