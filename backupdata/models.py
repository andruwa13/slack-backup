from datetime import datetime, timedelta
import json
from django.db import models

# Create your models here.
import re
import requests
from user_profile.models import User
import cgi
from math import *
import logging
from django.utils.dateformat import format

def crawl_all_channel(user):
    url = "https://slack.com/api/channels.list?token=" + user.slack_access_token
    r = requests.get(url)

    channels = parse_channel(user, json.loads(r.content)['channels'], False)

    url = "https://slack.com/api/groups.list?token=" + user.slack_access_token
    r = requests.get(url)

    groups = []

    return channels, groups


def parse_channel(user, json_channels, is_privategroup):
    channels = []

    for c in json_channels:
        channel, created = Channel.objects.get_or_create(slack_id=c['id'])
        channel.name = c['name']
        try:
            channel.topic = c['topic']['value']
        except:
            pass

        try:
            channel.purpose = c['purpose']['value']
        except:
            pass
        channel.is_archived = c['is_archived']
        channel.is_privategroup = is_privategroup
        channel.save()
        channels.append(channel)

        if is_privategroup:
            members = c.get('members',[])
            for m in members:
                if m == user.slack_id:
                    ChannelMember.objects.get_or_create(channel=channel, user=user)
        elif c.get('is_member', ''):
            ChannelMember.objects.get_or_create(channel=channel, user=user)

    return channels


def add_messages(messages, channel):
    for m in messages:
        ts = datetime.fromtimestamp(float(m.get('ts', 0)))

        user_slack_id = m.get('user', '')
        message_type = m.get('type', '')
        if user_slack_id != '' and message_type != '' and ts != None:
            message, created = Message.objects.get_or_create(user_slack_id=user_slack_id, message_type= message_type, ts=ts,
                                                             channel=channel)
            message.text = m.get('text', '')
            message.save()


class Channel(models.Model):
    name = models.CharField(max_length=100, default='')
    topic = models.TextField(default='', blank=True)
    purpose = models.TextField(default='')
    slack_id = models.CharField(max_length=10, default='')
    creator_slack_id = models.CharField(max_length=10, default='', blank=True)

    next_crawl_time = models.DateTimeField(auto_now_add=True)
    next_crawl_cycle = models.IntegerField(default=1)  # hours

    is_privategroup = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    latest_crawled = models.DateTimeField(null=True)
    oldest_crawled = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.name

    def get_creator(self):
        #print "self.name: " + self.name
        #print "self.creator_slack_id: " + self.creator_slack_id
        if self.creator_slack_id:
            u = User.objects.get(slack_id=self.creator_slack_id)
        else:
            u = ChannelMember.objects.filter(channel=self)
            if u.count() > 0:
                u = u[0].user
            else:
                u = None
        return u

    def crawl_history(self, verbose=False):

        logger = logging.getLogger(__name__)

        if self.get_creator() is None:
            # TODO improve, should use token of admin user
            print "Can't get creator for channel - " + self.name
            return
        else:
            token = self.get_creator().slack_access_token

        print "Parse channel: " + self.name
        epoch = datetime.fromtimestamp(0)

        if self.oldest_crawled is None:
            self.oldest_crawled = datetime.now()
            self.latest_crawled = datetime.now()
            self.save()

        while self.oldest_crawled > epoch:

            if self.is_privategroup == False:
                url = 'https://slack.com/api/channels.history'
            else:
                url = 'https://slack.com/api/groups.history'

            url += "?token=" + token

            url += "&channel=" + self.slack_id
            url += "&latest=" +  format(self.oldest_crawled, u'U') 

            r = requests.get(url)

            if verbose:
                logger.info(url)

            js = json.loads(r.content)

            messages = js['messages']
            if len(messages) > 0:
                latest =  messages[-1]['ts']
                has_more = js['has_more']
                if has_more:
                    self.oldest_crawled = datetime.fromtimestamp(float(latest))
                else:
                    self.oldest_crawled = datetime.fromtimestamp(0)



                add_messages(messages, self)


            else:
                self.oldest_crawled = datetime.fromtimestamp(0)
            self.save()

        now = datetime.now()

        while self.latest_crawled < now:

            if self.is_privategroup == False:
                url = 'https://slack.com/api/channels.history'
            else:
                url = 'https://slack.com/api/groups.history'

            url += "?token=" + token

            url += "&channel=" + self.slack_id
            url += "&oldest=" + format(self.latest_crawled, u'U') 

            self.latest_crawled = self.latest_crawled + timedelta(hours=12)
            if self.latest_crawled > now:
                self.latest_crawled = now
            self.save()

            url += "&latest=" + format(self.latest_crawled, u'U') 

            r = requests.get(url)
            js = json.loads(r.content)
            if 'error' in js:
                print "api error" + js['error']
                if js['error'] == 'token_revoked':
                    # bad scenario, should use some working token instead
                    # TODO improve
                    pass
                    #self.creator_slack_id = change to admin user
                    #self.save()
                return  False

            messages = js['messages']

            if len(messages) == 0:
                 self.latest_crawled = now
            else:
                add_messages(messages, self)




            self.save()

        self.next_crawl_time += timedelta(hours=self.next_crawl_cycle)
        self.save()


class ChannelMember(models.Model):
    channel = models.ForeignKey(Channel)
    user = models.ForeignKey(User)

    def __unicode__(self):
        name = ''
        if self.channel and self.channel.name:
            name += self.channel.name + " "
        if self.user and self.user.slack_username:
            name += self.user.slack_username

        return name


class Message(models.Model):
    message_type = models.CharField(max_length=50, default='', db_index=True)
    message_subtype = models.CharField(max_length=50, default='', db_index=True)
    hidden = models.BooleanField(default=False)
    ts = models.DateTimeField(null=True, db_index=True)
    deleted_ts = models.DateTimeField(null=True)
    event_ts = models.DateTimeField(null=True)

    user_slack_id = models.CharField(max_length=10, default='', db_index=True)
    user = models.ForeignKey(User, null=True)
    text = models.TextField(default='')

    channel = models.ForeignKey(Channel, null=True)

    def __unicode__(self):
        return self.get_text()

    def __str__(self):
        return self.get_text()


    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return  reverse('message', args=(self.id,))

    def get_user(self):
        if self.user is None:
            u = User.objects.filter(slack_id=self.user_slack_id)[0]
            self.user = u
            self.save()

        return self.user

    def unescape_html(self, html):
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&amp;', '&')
        return html

    def get_text(self):

        quote = re.compile('^&gt; (.*?)\n', re.MULTILINE|re.DOTALL)
        quote_results = quote.findall(self.text)
        #print self.text.encode('ascii', 'ignore')
       	for quote_m in quote_results:
            #print quote_m.encode('ascii', 'ignore')
            self.text = self.text.replace("&gt; " + quote_m + "\n", "<blockquote>" + quote_m + "</blockquote>" )


        pre = re.compile('```(.*?)```', re.MULTILINE|re.DOTALL)

        pre_results = pre.findall(self.text)

        for pre_m in pre_results:
            from pygments import highlight
            from pygments.lexers import guess_lexer
            from pygments.lexers.special import TextLexer
            from pygments.formatters import HtmlFormatter
            from pygments.util import ClassNotFound
            try:
                lexer = guess_lexer(self.unescape_html(pre_m[:2048]))
            except (ClassNotFound, ValueError):
                lexer = TextLexer()
            formatted =  highlight(self.unescape_html(pre_m), lexer, HtmlFormatter())
            self.text = self.text.replace("```" + pre_m + "```",  formatted )

        code = re.compile('`(.*?)`', re.MULTILINE|re.DOTALL)
        code_results = code.findall(self.text)

        for code_m in code_results:
            self.text = self.text.replace("`" + code_m + "`", "<code>" + code_m + "</code>" )

        p = re.compile('<(.*?)>')
        results = p.findall(self.text)
        for m in results:
            if m.startswith('@U'):
                slack_id = m.replace("@",'').split("|")[0]
                try:
                    user = User.objects.get(slack_id = slack_id)
                except:
                    user = None

                if user:
                    self.text = self.text.replace("<" + m + ">", user.slack_username )

            if m.startswith('http'):
                link = m.split("|")[0]
                try:
                    title = m.split("|")[1]
                except IndexError:
                    title = ''

                if False: #link.endswith(('png', 'jpg', 'jpeg', 'gif',)):
                    self.text = self.text.replace("<" + m + ">", "<a href='"+link + "' title='"+title+"'>" + "<img width=300px src='"+link+"'>" + "</a>" )
                else:
                    self.text = self.text.replace("<" + m + ">", "<a href='"+link + "' title='"+title+"'>" + link + "</a>" )


        return self.text

