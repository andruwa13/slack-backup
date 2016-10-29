from backupdata.models import Channel, Message, ChannelMember
from django.contrib import admin


def get_history(modeladmin, request, queryset):
    for obj in queryset:
        obj.crawl_history(True)
get_history.short_description = "Download history"

class ChannelAdmin(admin.ModelAdmin):
    actions = [get_history]
    list_display = ("name", "next_crawl_time", "latest_crawled", "oldest_crawled" ,"get_creator" )
    ordering = ('name',)

class MessageAdmin(admin.ModelAdmin):
    list_filter = ("channel", )
    ordering = ('-ts',)

# Register your models here.
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(ChannelMember)
