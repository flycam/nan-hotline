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
    def get_by_id(cls, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, sip_uri, supporter FROM supporter_phones WHERE id = %s;", (id,))
        res = cursor.fetchone()
        p = SupporterPhone()
        p.id = res[0]
        p.sip_uri = res[1]
        p.supporter = Supporter.get_by_id(res[2])
        return p

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
    def get_by_id(cls, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, telegram_id FROM supporters;")
        s = cursor.fetchone()
        supp = Supporter()
        supp.id = s[0]
        supp.name = s[1]
        supp.telegram_id = s[2]
        supp.phones = SupporterPhone.get_by_supporter(supp)
        return supp

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


def create_conversation(sip_uri, path):
    '''
    Create a new conversation
    :param sip_uri: caller sip uri
    :param path: wizard path
    :return: (case_id, call_id)
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO cases DEFAULT VALUES RETURNING id;")
    case_id = cursor.fetchone()[0]
    print("Created case with id {}".format(case_id))
    cursor.execute(
        """
        INSERT INTO wizard_calls ("case", "time", path, supportee_sip_uri)
        VALUES (%s, now(), %s, %s)
        RETURNING id;
        """,
        (case_id, path, sip_uri)
    )
    call_id = cursor.fetchone()[0]
    print("Created call with id {}".format(call_id))
    conn.commit()

    return case_id, call_id


def set_conversation_supporter(case_id, call_id, supporter_phone):
    if supporter_phone is not None:
        assigned_supporter_id = supporter_phone.supporter.id
        supporter_phone_id = supporter_phone.id
    else:
        assigned_supporter_id = None
        supporter_phone_id = None

    conn = get_db_connection()
    cursor = conn.cursor()

    print("Assigning supporter {} to case {} and call {}".format(assigned_supporter_id, case_id, call_id))

    cursor.execute("UPDATE cases SET (assigned_supporter) = (%s) WHERE id=%s;", (assigned_supporter_id, case_id))
    cursor.execute("UPDATE wizard_calls SET (supporter_phone) = (%s) WHERE id=%s;", (supporter_phone_id, call_id))
    conn.commit()


def create_proxy_call(case_id, target_sip_uri, supporter_phone_id):
    '''
    :param case_id:
    :param target_sip_uri:
    :return: call_id
    '''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO proxy_calls ("case", "time", target_sip_uri, supporter_phone)
        VALUES (%s, now(), %s, %s)
        RETURNING id;
        """,
        (case_id, target_sip_uri, supporter_phone_id)
    )
    call_id = cursor.fetchone()[0]
    print("Created proxy call with id {}".format(call_id))
    conn.commit()

    return call_id


def set_proxy_call_accepted(call_id, accepted):
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Setting proxy call {} accepted to {}".format(call_id, accepted))

    cursor.execute("UPDATE proxy_calls SET (accepted) = (%s) WHERE id=%s;", (accepted, call_id))
    conn.commit()

if __name__ == "__main__":
    sp = SupporterPhone()
    sp.id = 1
    create_conversation("not really a sip uri", "1->2")