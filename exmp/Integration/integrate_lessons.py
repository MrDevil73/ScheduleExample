import os
import sqlite3
import time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from exmp.models import Teacher, Group, Auditory, Lesson, LesTypes, SubGroup, TgUser
# print(*Teacher.objects.all(),sep='\n')
from exmp.utils import replace_group, replace_from_lat
from django.db import models
from django.db import connection
import time


def Main():
    def ConCur():
        con = sqlite3.connect("../storage/list.db")
        cur = con.cursor()
        return con, cur

    all_times = [0]
    main_timer = time.time()
    con, cur = ConCur()
    grp_ids = {}
    audit_ids = {}
    lestypes_ids = {}
    subgroups_ids = {}
    teacher_ids = {}

    created_grp = []
    created_audit = []
    created_teachers = []

    # CreteGroups
    sql_group = """SELECT DISTINCT group_name FROM lis order by group_name DESC"""
    cur.execute(sql_group)
    grp = [el for el, in cur.fetchall()]
    for el in grp:
        pretty_grp = replace_group(el)
        gro, created = Group.objects.get_or_create(name=pretty_grp)
        if created:
            gro.title_name = el.upper()
            gro.name = pretty_grp
            gro.save()
            created_grp.append(el)
        grp_ids[el] = gro.id
    print("Created groups:", created_grp)

    # CreteAudits
    sql_group = """SELECT DISTINCT audit FROM lis order by audit DESC"""
    cur.execute(sql_group)
    auds = [el for el, in cur.fetchall()]
    for au in auds:
        auda, created = Auditory.objects.get_or_create(name=au)
        if created:
            auda.name = au
            auda.save()
            # print("Created audit",au)
            created_audit.append(au)
        audit_ids[au] = auda.id
    print("Created audits:", created_audit)

    # Cretesubgroup
    sql_group = """SELECT DISTINCT subgroup FROM lis order by subgroup DESC"""
    cur.execute(sql_group)
    sbs = [el for el, in cur.fetchall()]
    for ss in sbs:
        sbg, created = SubGroup.objects.get_or_create(name=ss)
        if created:
            sbg.name = ss
            sbg.smile = "🐬"
            sbg.save()
            print("Created subgroup", sbg)
        subgroups_ids[ss] = sbg.id

    # CreteTyp
    sql_group = """SELECT DISTINCT type FROM lis order by type DESC"""
    cur.execute(sql_group)
    typs = [el for el, in cur.fetchall()]
    for tp in typs:
        lstp, created = LesTypes.objects.get_or_create(name=tp.capitalize().replace('1', '').strip())
        if created:
            lstp.name = tp.capitalize().replace('1', '').strip()
            lstp.smile = "🚪"
            lstp.save()
            print("Created LesType", lstp)
        lestypes_ids[tp] = lstp.id

    sql_group = """SELECT DISTINCT teacher FROM lis order by teacher DESC"""
    cur.execute(sql_group)
    teachs = [replace_from_lat(el) for el, in cur.fetchall()]
    for tc in teachs:
        teach, created = Teacher.objects.get_or_create(name=tc)
        if created:
            teach.name = tc
            teach.save()
            created_teachers.append(tc)
        teacher_ids[tc] = teach.id
    print("Created teachers", created_teachers)

    all_times.append(time.time() - main_timer - sum(all_times[:-1]))

    num_day = time.time() // 86400
    print("Previous day", num_day)
    ##################
    # Lesson.objects.filter(number_day__gt=num_day).exclude(type__name__icontains='коммент').delete()
    ##########################
    print(f"Lesson after {num_day} deleted")

    max_id = Lesson.objects.aggregate(max_id=models.Max('id'))['max_id']
    print(f"Максимум айди {max_id} ")
    max_id = max_id + 1 if max_id else 1

    # with connection.cursor() as cursor:
    #     cursor.execute(f"ALTER SEQUENCE ulspu_lesson_id_seq RESTART WITH {max_id};")

    xm_les = []

    def mini_help(st):
        st[7] = replace_from_lat(st[7])
        return st

    all_less_query = f"""SELECT DISTINCT * FROM lis WHERE number_day>{int(num_day)} ORDER BY number_day"""
    cur.execute(all_less_query)
    all_less = [mini_help(list(el)) for el in cur.fetchall() if int(el[0]) > int(num_day)]

    for les in all_less:
        try:
            obj, creat = Lesson.objects.get_or_create(number_day=int(les[0]), order_in_day=int(les[1]), group_id=grp_ids[les[2]], subgroup_id=subgroups_ids[str(les[3])],
                                                      discipline=les[4], audit_id=audit_ids[les[8]], type_id=lestypes_ids[les[5]])

            if creat:
                obj.teacher_id = teacher_ids[les[7]]
                obj.time_start = les[9]
                obj.time_finish = les[10]
            obj.save()
        except Exception as e:
            print(e)
    all_times.append(time.time() - main_timer - sum(all_times[:-1]))

    print(all_times)

if __name__ == '__main__':
    Main()
