from backupdata.models import crawl_all_channel, Channel, Message, ChannelMember, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from math import *

# Create your views here.
from django.template import RequestContext


def home(request):
    if request.user.is_authenticated():

        return HttpResponseRedirect('/team')
    variables = {}
    return render(request, 'index.html', variables)


@login_required
def stats(request):
    from django.db.models import Count, Sum
    from django.db.models.functions import Length
    import datetime 


    week   = ['Sunday', 
              'Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday']

    stats = []

    message_time_week_q = Message.objects.all().extra({"day": "strftime(\"%w\", \"ts\")"}).values("day")\
        .annotate(count=Count("id")).order_by('-count')

    message_hour_q = Message.objects.all().extra({"hour": "strftime(\"%H\", \"ts\")"}).values("hour")\
        .annotate(count=Count("id")).order_by('-count')

    message_time_q = Message.objects.all().extra({"hour": "strftime(\"%w_%H\", \"ts\")"}).values("hour")\
        .annotate(count=Count("id")).order_by('-count')

    channel_message_count_q = Message.objects.values('channel__name').annotate(count=Count('channel')).order_by('-count')
    user_by_text_length_q = User.objects.values('slack_username').annotate(text_len=Sum(Length('message__text'))).order_by('-text_len')
    user_by_message_count_q =  Message.objects.values('user__slack_username').annotate(count=Count('user__slack_username')).order_by('-count')


    stats.append(
        {
            'name': 'Message time by week day', 
            'items': [{'link': "",'name': week[int(stat['day'])], 'value': stat['count']} for stat in message_time_week_q],
            'total': message_time_q.aggregate(Sum('count'))['count__sum']
        }
    )


    stats.append(
        {
            'name': 'Message time by weekday+hour', 
            'items': [{'link': "",'name': week[int(stat['hour'].split("_")[0])]+" "+ stat['hour'].split("_")[1]+":00", 'value': stat['count']} for stat in message_time_q[:10]],
            'total': message_time_q.aggregate(Sum('count'))['count__sum']
        }
    )


    stats.append(
        {
            'name': 'Message time by hour', 
            'items': [{'link': "",'name': stat['hour']+":00", 'value': stat['count']} for stat in message_hour_q[:10]],
            'total': message_time_q.aggregate(Sum('count'))['count__sum']
        }
    )



    stats.append(
        {
            'name': 'Top channels', 
            'items': [{'link': "/channels/"+stat['channel__name'],'name': stat['channel__name'], 'value': stat['count']} for stat in channel_message_count_q[:10]],
            'total': channel_message_count_q.aggregate(Sum('count'))['count__sum']
        }
    )

    stats.append( 
        {
            'name': 'Top users by length', 
            'items': [{'link': "/team/"+stat['slack_username'],'name': stat['slack_username'], 'value': stat['text_len']} for stat in user_by_text_length_q[:10]],
            'total': user_by_text_length_q.aggregate(Sum('text_len'))['text_len__sum']
        }
    )

    stats.append( 
        {
            'name': 'Top users by message count', 
            'items': [{'link': "/team/"+stat['user__slack_username'],'name': stat['user__slack_username'], 'value': stat['count']} for stat in user_by_message_count_q[:10]],
            'total': user_by_message_count_q.aggregate(Sum('count'))['count__sum']
         }
    )

    return render(request, 'stats.html', {'stats': stats})



@login_required
def channels(request):
    channels, groups = crawl_all_channel(request.user)
    variables = {'channels': channels, 'groups': groups}
    return render(request, 'channels.html', variables)


@login_required
def channel_detail(request, channel_id):
    channel = Channel.objects.get(id=channel_id)

    messages = Message.objects.filter(channel=channel).order_by('-ts')
    variables = {'channel': channel, 'messages': messages}
    return render(request, 'channel.html', variables)

@login_required
def channel_message(request, message_id):
    message = Message.objects.get(id=message_id)
    from django.shortcuts import redirect
    from django.core.urlresolvers import reverse
    messages_count = Message.objects.filter(channel=message.channel, ts__gte=message.ts).order_by('-ts').count()
    page = int(ceil(float(messages_count) / float(100)))

    return  redirect("{0}?page={1}#message-{2}".format(reverse('channels', args=(message.channel.name,)), page, message.id))


@login_required
def channel_detail_name(request, channel_name):
    channel = Channel.objects.get(name=channel_name)

    messages = Message.objects.filter(channel=channel).order_by('-ts')
    variables = {'channel': channel, 'messages': messages}
    return render(request, 'channel.html', variables)

@login_required
def user(request, username):
    user = User.objects.get(slack_username=username )
    messages = Message.objects.filter(user_slack_id=user.slack_id).order_by('-ts')
    variables = {'user': user, 'messages': messages}
    return render(request, 'user.html', variables)



@login_required
def team(request):
    user = request.user

    team = user.get_team()
    members = team.parse_members()

    variables = {'members': members}
    return render(request, 'members.html', variables)
