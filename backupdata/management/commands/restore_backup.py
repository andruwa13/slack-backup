from backupdata.models import Channel,add_messages
import os
import json
import glob

import datetime

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        now = datetime.datetime.now()

        folder = "/usr/local/src/slack-backup/full_history/"

        data = {}
        with open(folder+'channels.json', 'r') as channels_file:
            data=channels_file.read()

        channels = json.loads(data)
        for c in channels:
            print(c['name'])

            channel, channel_created = Channel.objects.get_or_create(slack_id=c['id'])
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
            channel.is_privategroup = False
            channel.save()

            os.chdir(folder+c['name'])
            channel_files = glob.glob("*.json")
            channel_files.sort(key=lambda x: os.stat(os.path.join(folder+c['name'], x)).st_mtime)
            for file in channel_files:
                with open(folder+c['name']+"/"+file, 'r') as channel_file:
                    data=channel_file.read()

                messages = json.loads(data)
                add_messages(messages, channel)

