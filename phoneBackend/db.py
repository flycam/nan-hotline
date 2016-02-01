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


def create_conversation(supporter_phone, sip_uri, path):
    conn = get_db_connection()
    cursor = conn.cursor()

    if supporter_phone is not None:
        assigned_supporter_id = supporter_phone.supporter.id
        supporter_phone_id = supporter_phone.id
    else:
        assigned_supporter_id = None
        supporter_phone_id = None

    cursor.execute("INSERT INTO cases (assigned_supporter) VALUES (%s) RETURNING id;", (assigned_supporter_id,))
    case_id = cursor.fetchone()[0]
    print("Created case with id {}".format(case_id))
    cursor.execute(
        """
        INSERT INTO wizard_calls ("case", "time", path, supportee_sip_uri, supporter_phone)
        VALUES (%s, now(), %s, %s, %s)
        RETURNING id;
        """,
        (case_id, path, sip_uri, supporter_phone_id)
    )
    call_id = cursor.fetchone()[0]
    print("Created call with id {}".format(call_id))
    conn.commit()

if __name__ == "__main__":
    sp = SupporterPhone()
    sp.id = 1
    create_conversation(None, "not really a sip uri", "1->2")