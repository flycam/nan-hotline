import psycopg2
import threading
import serverconfig


thread_local = threading.local()


class SupporterPhone(object):
    def __init__(self):
        self.id = None
        self.sip_uri = None
        self.supporter = None

    @classmethod
    def get_by_supporter(cls, supporter):
        supp_id = supporter.id
        conn = get_db_connection()
        cursor = conn.cursor()
        phones = []
        cursor.execute("SELECT id, sip_uri FROM supporter_phones WHERE supporter = %s;", (supp_id,))
        for res in cursor.fetchall():
            p = SupporterPhone()
            p.supporter = supporter
            p.id = res[0]
            p.sip_uri = res[1]
            phones.append(p)
        return phones

    def __str__(self):
        return '{}-{}'.format(self.id, self.sip_uri)


class Supporter(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.telegram_id = None
        self.phones = None

    @classmethod
    def get_all(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, telegram_id FROM supporters;")
        supporters = []
        for s in cursor.fetchall():
            supp = Supporter()
            supp.id = s[0]
            supp.name = s[1]
            supp.telegram_id = s[2]
            supp.phones = SupporterPhone.get_by_supporter(supp)
            supporters.append(supp)
        return supporters

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.id, self.name, self.telegram_id, map(str, self.phones))


def get_db_connection():
    global thread_local
    connection = getattr(thread_local, 'conn', None)
    if connection is None:
        connection = psycopg2.connect(host=serverconfig.sql_host, database=serverconfig.sql_db, user=serverconfig.sql_user, password=serverconfig.sql_pw)
        setattr(thread_local, 'conn', connection)
    return connection


def create_conversation():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cases DEFAULT VALUES RETURNING id;")
    case_id = cursor.fetchone()[0]
    print("Created case with id {}".format(case_id))
    cursor.execute("")

if __name__ == "__main__":
    res = Supporter.get_all()
    print(', '.join(map(str, res)))