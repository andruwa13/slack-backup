from backupdata.models import Channel, Message, ChannelMember, Export
from django.contrib import admin


def restore_backup(modeladmin, request, queryset):
    import zipfile
    import tempfile
    from backupdata.management.commands.restore_backup import restore_files

    for obj in queryset:
        tmp_directory = tempfile.mkdtemp()
        zip_ref = zipfile.ZipFile(obj.export.url, 'r')
        zip_ref.extractall(tmp_directory)
        zip_ref.close()
        restore_files(tmp_directory)



restore_backup.short_description = "Restore backup"

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

class ExportAdmin(admin.ModelAdmin):
    actions = [restore_backup]
    list_display = ("export", "uploaded")
    ordering = ('uploaded',)

# Register your models here.
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(ChannelMember)
admin.site.register(Export, ExportAdmin)
