from telebot.types import User as TelegramUser
from .VK.types import UserFromGet as VkontakteUser
from .logg import LoggEvent
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


# Create your models here.

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    title_name = models.CharField(max_length=32)

    def __str__(self):
        return self.title_name


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    smile = models.CharField(max_length=16, default="👨‍🏫")

    def __str__(self):
        return self.name


class Auditory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class LesTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    smile = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name}"


class SubGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.IntegerField(unique=True)
    smile = models.CharField(max_length=16, default='', blank=True)

    def __str__(self):
        return f"{self.name}"


class TgUser(models.Model):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    cookie_token = models.CharField(max_length=512, null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return (f"@{self.username}" if self.username else f"{self.first_name or ''} {self.last_name or ''}") + f"  ({self.user_id})"

    def create_or_update_user(self, tg_json: TelegramUser) -> 'TgUser':

        user, created = TgUser.objects.get_or_create(user_id=tg_json.id)
        if created or user.username != tg_json.username:
            user.username = tg_json.username or user.username
            user.first_name = tg_json.first_name or user.first_name
            user.last_name = tg_json.last_name or user.last_name
            user.phone_number = tg_json.__dict__.get('phone_number', None)
            user.save()
            if created:
                LoggEvent("TG", user.user_id, "NewUser", "New User")

        return user


class VkUser(models.Model):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    cookie_token = models.CharField(max_length=512, null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}  @{self.username}"
        # return f"{self.user_id or self.first_name + self.last_name}"

    def create_or_update_user(self, vk_json: VkontakteUser) -> 'VkUser':
        user, created = VkUser.objects.get_or_create(user_id=vk_json.id)
        if created:
            user.username = vk_json.username or user.username
            user.first_name = vk_json.first_name or user.first_name
            user.last_name = vk_json.last_name or user.last_name
            user.save()
            LoggEvent("VK", user.user_id, "NewUser", "New User")

        return user


class Lesson(models.Model):
    number_day = models.IntegerField()
    order_in_day = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    subgroup = models.ForeignKey(SubGroup, on_delete=models.SET_NULL, null=True)
    discipline = models.CharField(max_length=256)
    type = models.ForeignKey(LesTypes, on_delete=models.SET_NULL, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    audit = models.ForeignKey(Auditory, on_delete=models.SET_NULL, null=True, blank=True)
    time_start = models.TimeField(null=True)
    time_finish = models.TimeField(null=True)

    def __str__(self):
        return f"{self.discipline} ({self.group})"


@receiver(pre_save, sender=TgUser)
def update_fields(sender, instance: TgUser, **kwargs):
    pass
    # old_inst=TgUser.objects.filter(user_id=instance.user_id).first()
    # if old_inst:
    #     if old_inst.group_id==None and instance.group_id!=None:
    #         instance.teacher=None
    #     elif old_inst.teacher_id==None and instance.teacher_id!=None:
    #         instance.group=None
    #     elif instance.group_id and instance.teacher_id:
    #         instance.teacher=None
