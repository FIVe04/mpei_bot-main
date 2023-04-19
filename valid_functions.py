import time

VALID_ARR = [chr(i) for i in range(1072, 1104)] + [chr(i) for i in range(1040, 1072)]


def check_valid_str(s):
    if not s or not (all([bool(i in VALID_ARR) for i in s])):
        return 'Это не похоже на имя. Попробуйте ещё раз. '
    if len(s) > 100:
        return 'Строка должна быть не длиннее 25 символов. Попробуйте ещё раз.'
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
        valid_date = time.strptime(date, '%m.%d.%Y')
        return True
    except ValueError:
        return 'Введите дату в формате дд.мм.гггг '


def check_time(mero_time):
    try:
        valid_mero_time = time.strptime(mero_time, format='%H:%M')
        return True
    except ValueError:
        return 'Введите время начала в формате чч:мм '
