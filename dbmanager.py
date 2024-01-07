import datetime
import pymysql, hashlib


def getError(exception):
    return str(exception).replace('(', '').replace(')', '').split(',')[0]


class dbm:

    def __init__(self, username, password, host, db_name):
        self.username, self.password, self.host, self.db_name = username, password, host, db_name

    def connect(self):
        self.connection = None
        self.connection = pymysql.connect(
            host=self.host,
            port=3306,
            user=self.username,
            password=self.password,
            database=self.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        return bool(self.connection)

    def close(self):
        try:
            self.connection.close()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, ex]

    def registered(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select username from `users` where id=%s""", (discordID,))
                return [True, False if cursor.fetchone() is None else True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def getUsernameByDiscordID(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""SELECT username FROM `users` WHERE id = %s""", (discordID,))
                return [True, cursor.fetchone()]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def register(self, discordID, username, password, birthday):
        try:
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            data = datetime.date.today() + datetime.timedelta(days=7)
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """insert into `users` (id, username, password, birthday) values (%s, %s, %s, %s)""", (discordID, username, password, birthday,))
                cursor.execute("""insert into `store` (id, data_trial) values (%s, %s)""", (discordID, data,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def changePassword(self, discordID, password):
        try:
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            with self.connection.cursor() as cursor:
                cursor.execute("""update `users` set password = %s where id=%s""", (password, discordID,))
                self.connection.commit()
                return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def changeUsername(self, discordID, username):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select username from `users` where id=%s""", (discordID,))
                name = cursor.fetchone()
                cursor.execute("""update `users` set username = %s where id=%s""", (username, discordID,))
                self.connection.commit()
                return [True, name]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def save_pay(self, discordID, invoice_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""update `store` set invoice_id = %s where id= %s""", (invoice_id, discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def check_pay(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select invoice_id from `store` where id=%s""", (discordID,))
                self.connection.commit()
                return [True, cursor.fetchone()]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]
    
    def delete_pay(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """update `store` set invoice_id = NULL where id=%s""", (discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def check_money(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select money from `store` where id = %s""", (discordID,))
                self.connection.commit()
            return [True, cursor.fetchone()]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def add_money(self, discordID, money):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""update `store` set money = `money` + %s where id= %s""", (money, discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def add_money_username(self, username, money):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select id from `users` where username=%s""", (username,))
                discordID = cursor.fetchone()['id']
                cursor.execute("""update `store` set money = `money` + %s where id=%s""", (money, discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def remove_money(self, discordID, money):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""update `store` set money = `money` - %s where id=%s""", (money, discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def check_date(self, data):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select id from `store` where data_trial=%s""", (data,))
                self.connection.commit()
            return cursor.fetchall()
        except Exception as ex:
            print(ex)
            return [None]

    def check_date_all(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('select id, data_trial from `store`')
                self.connection.commit()
            return cursor.fetchall()
        except Exception as ex:
            print(ex)
            return [None]

    def add_data(self, data, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""update `store` set data_trial=%s where id=%s""", (data, discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def remove_data(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""update `store` set data_trial = NULL where id=%s""", (discordID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def unbane(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select hwidId from `users` where id=%s""", (discordID,))
                ID = cursor.fetchone()['hwidId']
                cursor.execute("""update `hwids` set banned = 0 where id=%s""", (ID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def bane(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select hwidId from `users` where id=%s""", (discordID,))
                ID = cursor.fetchone()['hwidId']
                cursor.execute("""update `hwids` set banned = 1 where id=%s""", (ID,))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def check_hwidId(self, discordID):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select hwidId from `users` where id=%s""", (discordID,))
                self.connection.commit()
            return cursor.fetchone()
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def check_discordID_toInvoice_id(self, invoice_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select id from `store` where invoice_id=%s""", (invoice_id,))
                self.connection.commit()
            return [True, cursor.fetchone()]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def check_promo(self, code):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select id, enabled from `promo` where code = %s""", (code,))
                self.connection.commit()
                res = cursor.fetchone()
            return [True, res if res is not None else {'enabled': 0}]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]

    def add_use_promo(self, code):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""update `promo` set `use`= `use` + 1 where code= %s""", (code, ))
                self.connection.commit()
            return [True]
        except Exception as ex:
            print(ex)
            return [False, getError(ex)]
        
    def check_uuid(self, nickname):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""select uuid from `users` where username=%s""", (nickname,))
                self.connection.commit()
            return cursor.fetchall()
        except Exception as ex:
            print(ex)
            return [None]