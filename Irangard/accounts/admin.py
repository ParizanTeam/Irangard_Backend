from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Verification)
admin.site.register(Token)
