from django.contrib import admin
from .models import MemoryLog

def direct_admin_delete(modeladmin, request, queryset):
    # for item in queryset.all():
    #     item.delete()
    if queryset.count() > 0:
        from django.db import connection
        cursor = connection.cursor()
        try:
            selected_items = str(list(queryset.all().values_list('log_id', flat=True)))[1:-1]
            sql = 'DELETE FROM logger_logger WHERE log_id IN (%s)' % selected_items
            # cursor.execute("BEGIN")
            cursor.execute(sql)
            # cursor.execute("COMMIT")
        finally:
            cursor.close()

direct_admin_delete.short_description = "Rapid Delete Selected Items"

class MemoryLogAdmin(admin.ModelAdmin):
    list_filter = ('created_at', 'location', 'size_kb', 'count')
    list_display = ('created_at', 'location', 'size_kb', 'count')
    actions = [direct_admin_delete]


admin.site.register(MemoryLog, MemoryLogAdmin)
