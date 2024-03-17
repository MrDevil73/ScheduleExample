from .VK.VkMain import TOKEN
from .VK.types import Bot
from .models import Group, Teacher, TgUser, Lesson, Auditory, SubGroup, LesTypes, VkUser
# Register your models here.
import os

from django.contrib import admin
from django.utils.html import format_html
import subprocess

from django.contrib.admin import AdminSite

from django.contrib import admin


class MyAppAdminSite(AdminSite):
    site_header = 'Админка'
    site_title = 'Админ Колледжа'
    index_title = 'Welcome to My App Admin'
    list_filter = ['Lesson']


class ItemLesson(admin.ModelAdmin):
    list_display = ['number_day', 'order_in_day', 'group', 'subgroup', 'discipline', 'teacher', 'audit', 'time_start', 'time_finish']
    list_filter = ['group', 'number_day', 'teacher']

    actions = ['run_script']

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


class ForTgUser(admin.ModelAdmin):
    readonly_fields = ('user_id',)
    search_fields = ['user_id', 'first_name', 'last_name', 'username']

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


class ForGroups(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


admin_site = MyAppAdminSite(name='exmp_appadmin')

admin_site.register(Group, ForGroups)
admin_site.register(Teacher)
admin_site.register(Auditory)
admin_site.register(Lesson, ItemLesson)
admin_site.register(TgUser, ForTgUser)
admin_site.register(SubGroup)
admin_site.register(LesTypes)


class ForVkUsers(admin.ModelAdmin):
    # Определение вашего административного класса
    readonly_fields = ('user_id',)
    actions = ['update_information']
    search_fields = ['user_id', 'first_name', 'last_name', 'username']

    @admin.action(description="Обновить данные")
    def update_information(self, request, queryset=None):
        bot = Bot(token=TOKEN)

        vk_users = VkUser.objects.all().values('user_id')
        CNT = 0
        for i in range(len(vk_users) // 100 + 1):
            elems = bot.users_get([el['user_id'] for el in vk_users[i * 100:(i + 1) * 100]])

            for elem in elems:
                vkus, created = VkUser.objects.get_or_create(user_id=elem['id'])

                if created or vkus.first_name != elem['first_name'] and elem != "DELETED" or vkus.last_name != elem['last_name']:
                    vkus.first_name = elem['first_name']
                    vkus.last_name = elem['last_name']
                    vkus.username = elem['domain']
                    vkus.save()
                CNT += 1
        self.message_user(request, f"Обновлена информация о {CNT} пользователях")
        return None

    update_information.short_description = "Обновить Пользователей ВК"
    update_information.allowed_permissions = ('change',)

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


admin_site.register(VkUser, ForVkUsers)
