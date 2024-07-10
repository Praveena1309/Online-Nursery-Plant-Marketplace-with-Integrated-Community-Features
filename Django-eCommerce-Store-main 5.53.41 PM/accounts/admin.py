from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile


class AccountAdmin(UserAdmin):
  
    readonly_fields = ['date_joined', 'last_login','email','last_login' , 'username', 'first_name', 'last_name', 'Phone_number']
    ordering = ('-date_joined_for_format',)
    list_filter = ['is_active']


    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove the password field from the form
        form.base_fields.pop('password', None)
        return form 

admin.site.register(Account, AccountAdmin)


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     def thumbnail(self, object):
#         return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
#     thumbnail.short_description = 'Profile Picture'
#     list_display = ('thumbnail', 'user', 'city', 'state', 'country')
