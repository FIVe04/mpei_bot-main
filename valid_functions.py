import datetime
import time
from data import *

VALID_ARR = [chr(i) for i in range(1072, 1104)] + [chr(i) for i in range(1040, 1072)]
VALID_ARR_2 = [chr(i) for i in range(1072, 1104)] + [chr(i) for i in range(1040, 1072)] + \
              [' '] + [chr(i) for i in range(48, 58)] + [chr(i) for i in range(97, 123)] + \
              [chr(i) for i in range(65, 91)]


def check_valid_str(s):
    if not s or not (all([bool(i in VALID_ARR) for i in s])):
        return 'Это не похоже на имя. Попробуйте ещё раз. '
    if len(s) > 100:
        return 'Строка должна быть не длиннее 100 символов. Попробуйте ещё раз.'
    return True


def check_mero_name(s):
    if not s or not (all([bool(i in VALID_ARR_2) for i in s])):
        return 'Это не похоже на имя мероприятия. Попробуйте ещё раз. '
    if len(s) > 100:
        return 'Строка должна быть не длиннее 100 символов. Попробуйте ещё раз.'
    return True


def check_group_number(group_num):
    if not (group_num[1] == '-' or group_num[2] == '-') or not (group_num[4] == '-' or group_num[5] == '-'):
        return 'Неверный номер группы! Он должен выглядеть, например, так А-01-22.' \
               'Попробуйте ещё раз. Используйте русскую раскладку'
    else:
        group_num = group_num.split('-')
        if not(all([bool(i in VALID_ARR) for i in group_num[0]])) or \
                not (all([bool(ord(i) in range(48, 58)) for i in group_num[1] + group_num[2]])):
            return 'Неверный номер группы! Он должен выглядеть, например, так А-01-22. ' \
                   'Попробуйте ещё раз. Используйте русскую раскладку'
    return True


def check_date(date):
    try:
        valid_date = datetime.datetime.strptime(date, '%d.%m.%Y')
        iso_date = valid_date.strftime('%Y-%m-%d')
        return True, iso_date
    except ValueError:
        return False, 'Введите дату в формате дд.мм.гггг '


def check_time(mero_time):
    try:
        valid_mero_time = datetime.datetime.strptime(mero_time, '%H:%M')
        iso_time = valid_mero_time.strftime('%H:%M')
        return True, iso_time
    except ValueError:
        return False, 'Введите время начала в формате чч:мм '


def check_date_and_time(mero_date, mero_time):
    now = datetime.datetime.now()
    if now.date() < datetime.datetime.strptime(mero_date, '%Y-%m-%d').date():
        return True
    if now.date() == datetime.datetime.strptime(mero_date, '%Y-%m-%d').date():
        if now.time() < datetime.datetime.strptime(mero_time, '%H:%M').time():
            return True
        return False
    return False


def check_if_can_add_mero_in_db(db, mero_date, mero_time, duration):
    events_date_and_time = db.get_events_date_and_time(mero_date)
    a = sorted(events_date_and_time, key=lambda e: e[0])
    mero_time_in_minutes = int(mero_time.split(':')[0]) * 60 + int(mero_time.split(':')[1])

    for i in range(len(a) - 1):
        time1 = int(a[i][0].split(':')[0]) * 60 + int(a[i][0].split(':')[1])
        time2 = int(a[i + 1][0].split(':')[0]) * 60 + int(a[i + 1][0].split(':')[1])
        if (time1 <= mero_time_in_minutes <= time2) and \
                not((time1 + a[i][1] < mero_time_in_minutes) and (mero_time_in_minutes + duration < time2)):
            return False
    return True


db = DbHelper()
print(check_if_can_add_mero_in_db(db, '2023-04-21', '14:30', 60))

