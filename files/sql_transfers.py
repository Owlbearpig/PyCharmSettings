import pymysql
from files import variables

class MysqlTransfer():

    def __init__(self):
        self.vars = variables.Variables()

        login = self.vars.get_mysql_login()
        user = login[0]
        pw = login[1]

        self.connection = pymysql.connect(host='192.168.2.79',
                             user=user,
                             password=pw,
                             db='wow_tb_members',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def store(self, data, single_store=True, table ="all_members"):
        with self.connection.cursor() as cursor:
            sql = "REPLACE INTO `{}` (`name`, `realm`, `class`, `level`, `achieve_pts`, `g_rank`, `achieve_id`) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(table)
            try:
                cursor.execute(sql, data)

            except Exception as e:
                print("last executed:",cursor._last_executed)
                print(e)
        if single_store:
            self.connection.commit()

    def versatile_db_store(self, single_store=True, table="member_links", **kwargs):
        keys = "("
        positions = "("
        for key in kwargs:
            keys += "`{}`".format(key) + ", "
            positions += "%s,"
        keys = keys[0:len(keys) - 2] + ")"
        positions = positions[0:len(positions) - 1] + ")"

        sql_cmd = "REPLACE INTO `{0}` {1} VALUES {2}".format(table, keys, positions)

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql_cmd, list(kwargs.values()))
            except Exception as e:
                print("last executed:", cursor._last_executed)
                print(e)
            if single_store:
                self.connection.commit()

    def db_get(self, table, column, sql_cond):
        res = None
        with self.connection.cursor() as cursor:
            sql = "SELECT `{0}` FROM `{1}` WHERE {2}"
            try:
                cursor.execute(sql.format(str(column), str(table), str(sql_cond)))
                res = cursor.fetchone()
            except Exception as e:
                print("last executed:", cursor._last_executed)
                print(e)
        return res

    def db_get_table(self, table):
        res = None
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `{0}`"
            try:
                cursor.execute(sql.format(str(table)))
                res = cursor.fetchall()
            except:
                pass
        return res

    def remove_entry(self, table, sql_cond):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM `{0}` WHERE {1}"
            try:
                cursor.execute(sql.format(str(table), str(sql_cond)))
            except:
                pass
        self.connection.commit()