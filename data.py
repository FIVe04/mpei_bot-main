import sqlite3
import datetime


class DbHelper:
    def __init__(self, dbname='data.db'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def add_person(self, telegram_id, name, surname, group_num):
        if not surname:
            surname = ' '
        self.conn.execute('INSERT INTO people VALUES (?, ?, ?, ?, ?)', (telegram_id, name, surname, group_num, 0))
        self.conn.commit()

    def person_in_db(self, telegram_id):
        if self.conn.execute('SELECT * FROM people WHERE telegram_id = ?', (telegram_id, )).fetchone():
            return True
        return False

    def if_admin(self, telegram_id):
        return self.conn.execute('SELECT admin FROM people WHERE telegram_id = ?', (telegram_id, )).fetchone()[0]

    def add_admin(self, telegram_id):
        self.conn.execute('UPDATE people SET admin = 1 WHERE telegram_id = ?', (telegram_id, ))
        self.conn.commit()

    def add_event(self, name, count, date, time, duration):
        self.conn.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)", (None, name, count, date, time, duration))
        self.conn.commit()

    def get_events_date_and_time(self, date):
        return self.conn.execute("SELECT time, duration FROM events WHERE (date = ?) AND (count >= 0)",
                                 (date,)).fetchall()

    def show_events(self):
        return self.conn.execute("SELECT * FROM events WHERE (date >= ?) AND (count >= 0)",
                                 (datetime.date.today(), )).fetchall()

    def unsubsribe_from_even(self, event_id, telegram_id):
        self.conn.execute("DELETE FROM registration WHERE event_id = ? and telegram_id = ? ", (event_id, telegram_id))
        self.conn.execute("UPDATE events SET count = count + 1 WHERE id = ?", (event_id,))

    def get_event_name(self, event_id):
        return self.conn.execute("SELECT name FROM events WHERE id = ?", (event_id, )).fetchone()

    def del_events(self):

        self.conn.execute('DELETE FROM registration WHERE event_id IN (SELECT id FROM events WHERE date < ?)',
                          (datetime.datetime.today() - datetime.timedelta(days=1), ))
        self.conn.execute('DELETE FROM events WHERE date < ?', (datetime.date.today() - datetime.timedelta(days=1), ))
        self.conn.commit()

    def get_number_of_available_seats(self, event_id):
        return self.conn.execute('SELECT count FROM events WHERE id = ?', (event_id, )).fetchone()

    def if_registration(self, event_id, telegram_id):
        a = self.conn.execute('SELECT * FROM registration WHERE (event_id = ?) AND (telegram_id = ?)',
                              (event_id, telegram_id)).fetchone()
        if not a:
            return True
        return False

    def add_registration(self, event_id, telegram_id):
        self.conn.execute('INSERT INTO registration VALUES (?, ?)', (event_id, telegram_id))
        self.conn.execute('UPDATE events SET count = count - 1 WHERE id = ?', (event_id, ))
        self.conn.commit()

    def get_my_registrations(self, telegram_id):
        return self.conn.execute('SELECT * FROM events WHERE id IN '
                                 '(SELECT event_id FROM registration WHERE telegram_id = ?)',
                                 (telegram_id, )).fetchall()

    def get_guests(self, event_id):
        return self.conn.execute('SELECT * FROM people WHERE telegram_id IN '
                                 '(SELECT telegram_id FROM registration WHERE event_id = ?)', (event_id, )).fetchall()
