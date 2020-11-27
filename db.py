from MySQLdb import *
import MySQLdb
import pymysql.cursors

#host = 'localhost'
new_user_busy = 0
new_group_busy = 0
update_user_busy = 0
update_group_busy = 0

class DB:
    conn = None
    def connect(self):
        self.conn = pymysql.connect(host = host,user = "user",password = "password",db = "database")
    def query(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor
    def commit(self):
        try:
            self.conn.commit()
        except:
            self.connect()
            self.conn.commit()

db = DB()


def new_user(*argv):
    global new_user_busy
    new_user_busy = 1
    try:
        userid = argv[0]
    except:
        userid = False
    try:
        is_infected = argv[1]
    except:
        is_infected = False
    try:
        mask_on = argv[2]
    except:
        mask_on = False
    try:
        infected_by = argv[3]
    except:
        infected_by = False
    try:
        users_infected = argv[4]
    except:
        users_infected = False
    if userid and is_infected and mask_on:
        sql = "Insert into tgusers (userid,is_infected,mask_on) values ({},{},{})".format(userid,is_infected,mask_on)
        a = db.query(sql)
        db.commit()
  
    if userid and is_infected == False and mask_on == False:
        sql = "Insert into tgusers (userid) values ({})".format(userid)
        db.query(sql)
        db.commit()
    print("Executed New User ID :{}".format(argv[0]))
    new_user_busy = 0

def new_group(a,b,c,*args):
    global new_group_busy
    new_group_busy = 1
    if args:
        d = args[0]
    try:
        a = d
        sql = "Insert into groups(chatid,sneezed,sneeze_remaining,sneezed_by) values ({},{},{},{})".format(a,b,c,d)
    except:
        sql = "Insert into groups(chatid,sneezed,sneeze_remaining) values ({},{},{})".format(a,b,c)
    db.query(sql)
    db.commit()
    print("Executed New Group ID: {}".format(a))
    new_group_busy = 0

def check_user(id):
    sql = "Select * from tgusers where userid = {}".format(id)
    a = db.query(sql)
    r = a.fetchall()
    if r:
        return r[0]
    else:
        return False
    print("Check USer ID: {}".format(id))

def check_group(id):
    sql = "Select * from groups where chatid = {}".format(id)
    a = db.query(sql)
    r = a.fetchall()
    if r:
        return r[0]
    else:
        return False
    print("CHeck Group ID: {}".format(id))


def update_group(a,b,c,d):
    global update_group_busy
    update_group_busy = 1
    sql = str("Update groups SET ")
    if a:
        end = 'WHERE chatid = "{}"'.format(a)
    else:
        return False
    if b != 'n':
        if c != 'n':
            sql = str(sql)+"sneezed = {},".format(b)
        else:
            sql = str(sql)+"sneezed = {} ".format(b)
    else:
        pass
    if c != 'n':
        sql = (sql)+"sneeze_remaining = {} ".format(c)
    else:
        pass
    if d != 'n':
        if c!= 'n':
            sql = (sql)+',sneezed_by = "{}" '.format(d)
        else:
            sql = (sql)+'sneezed_by = "{} " '.format(d)
    else:
        pass
    sql = sql+end
    print(sql)
    db.query(sql)
    db.commit()
    update_group_busy = 0

def update_user(a,b,c,d,*args):
    global update_user_busy
    update_user_busy = 1

    sql = str("Update tgusers SET ")
    if a:
        end = 'WHERE userid = "{}"'.format(a)
    else:
        return False
    if b != 'n':
        if c != 'n':
            sql = str(sql)+"is_infected = {},".format(b)
        else:
            sql = str(sql)+"is_infected = {} ".format(b)
    else:
        pass
    if c != 'n':
        sql = str(sql)+"mask_on = {} ".format(c)
    else:
        pass
    if d != 'n':
        if (c!= 'n') or (b!='n'):
            sql = str(sql)+',infected_by = "{}" '.format(d)
        else:
            sql = str(sql)+'infected_by = "{} " '.format(d)
    else:
        pass
    if args:
        e = args[0]
        if (b!='n') or (c!='n') or (d!='n'):
            sql = str(sql)+',users_infected = "{}" '.format(e)
        else:
            sql = str(sql)+'users_infected = "{}" '.format(e)
    sql = sql+end
    print(sql)
    db.query(sql)
    db.commit()
    update_user_busy = 0

def check_news(chat_id):
    sql = 'Select * from autonews where chatid = {}'.format(chat_id)
    a = db.query(sql)
    r = a.fetchall()
    if r:
        return r[0]
    else:
        return False

def create_auto_news(chatid,*args):
    if args:
        ison = int(args[0])
        sql = 'Insert into autonews(chatid,ison) values({},{})'.format(chatid,ison)
    else:
        args = False
        sql = 'insert into autonews(chatid) values({})'.format(chatid)
    db.query(sql)
    db.commit()

def update_news(chatid,value,country):
    sql = str("Update autonews SET ")
    if chatid:
        pass
    else:
        return False
    end = str("Where chatid = {}").format(chatid)
    if value != 'n':
        sql = sql+"ison = {} ".format(value)
    if country != 'n':
        if value!='n':
            sql = sql+',country = "{}" '.format(country)
        else:
            sql = sql+'country = "{}" '.format(country)
    sql = sql+end
    print(sql)
    db.query(sql)
    db.commit()


def userislive(id,value):
    sql = 'Update tgusers set isactive = {} where userid = {}'.format(value,id)
    db.query(sql)
    db.commit()


def groupislive(id,value):
    sql = 'Update groups set isactive = {} where chatid = {}'.format(value,id)
    db.query(sql)
    db.commit()
