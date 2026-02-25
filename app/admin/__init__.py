from django.contrib import admin

from app.models import Account, User

admin.site.register(User)
admin.site.register(Account)
