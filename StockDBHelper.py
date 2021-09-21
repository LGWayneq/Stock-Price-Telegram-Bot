import sqlite3

class DBHelper:
    def __init__(self, dbname="gmebottime.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
    
    def createTable(self):
        cmd = "CREATE TABLE IF NOT EXISTS reminders (description text, owner text)"
        cmd2 = "CREATE TABLE IF NOT EXISTS remindertime (owner text PRIMARY KEY, timeinterval int)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON reminders (owner ASC)"
        self.conn.execute(cmd)
        self.conn.execute(cmd2)
        self.conn.execute(ownidx)
        self.conn.commit()
    
    def activeChats(self):
        cmd = "SELECT owner FROM reminders GROUP BY owner"
        return [x[0] for x in self.conn.execute(cmd)]
    
    def setTime(self, owner, time):
        timeinterval = time
        cmd = "INSERT OR IGNORE INTO remindertime (owner, timeinterval) VALUES (?, ?, ?)"
        cmd2 = "UPDATE remindertime SET usertimehr = (?) WHERE owner = (?)"
        arg = (owner,timeinterval)
        arg2 = (timeinterval,owner)
        self.conn.execute(cmd,arg)
        self.conn.execute(cmd2,arg2)
        self.conn.commit()
    
    def checkTime(self, owner):
        cmdtime = "SELECT timeinterval FROM remindertime WHERE owner = (?)"
        arg = (owner, )
        mins = [x[0] for x in self.conn.execute(cmdtime, arg)]
        return (mins[0])
        
        