import sqlite3

class DBHelper():
    def __init__(self, dbname="stockBotDB.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread = False)
    
    def createTable(self):
        cmd = "CREATE TABLE IF NOT EXISTS alerts (owner_id INTEGER PRIMARY KEY, alert BOOLEAN)"
        cmd2 = "CREATE TABLE IF NOT EXISTS pastTickers (owner_id INTEGER PRIMARY KEY, first_ticker TEXT, second_ticker TEXT, last_ticker TEXT)"
        self.conn.execute(cmd)
        self.conn.execute(cmd2)
        self.conn.commit()
        
    
    def checkAlerts(self, owner):
        cmd = "SELECT alert FROM alerts WHERE owner_id = (?)"
        arg = (owner, )
        alerts = [x[0] for x in self.conn.execute(cmd, arg)][0]
        return alerts
    
    def getAllAlerts(self):
        cmd = "SELECT owner_id FROM alerts WHERE alert = (?)"
        arg = (1,)
        alerts = [x[0] for x in self.conn.execute(cmd, arg)]
        return alerts
    
    def setAlerts(self, owner, alert_bool):
        try:
            ownerid = [x[0] for x in self.conn.execute("SELECT owner_id FROM alerts WHERE owner_id = (?)", (owner,))][0]
            cmd = "UPDATE alerts SET alert = (?) WHERE owner_id = (?)"
            arg = (alert_bool, owner)
        except:
            cmd = "INSERT INTO alerts VALUES ((?),(?))"
            arg = (owner, alert_bool)
        self.conn.execute(cmd, arg)
        self.conn.commit()
    
        
    def updatePastTickers(self, owner, ticker):
        try:
            ownerid = [x[0] for x in self.conn.execute("SELECT owner_id FROM pastTickers WHERE owner_id = (?)", (owner,))][0]
            first_ticker = [x[0] for x in self.conn.execute("SELECT first_ticker FROM pastTickers WHERE owner_id = (?)", (owner,))][0]
        except:
            cmd = "INSERT INTO pastTickers VALUES((?),(?),(?),(?))"
            arg = (owner, ticker, None, None)
            self.conn.execute(cmd, arg)
            self.conn.commit()
            return
        second_ticker = [x[0] for x in self.conn.execute("SELECT second_ticker FROM pastTickers WHERE owner_id = (?)", (owner,))][0]
        last_ticker = [x[0] for x in self.conn.execute("SELECT last_ticker FROM pastTickers WHERE owner_id = (?)", (owner,))][0]
        if second_ticker == None and ticker != first_ticker:
            cmd = "UPDATE pastTickers SET second_ticker = (?) WHERE owner_id = (?)"
            arg = (ticker, owner)
        elif last_ticker == None and ticker != first_ticker and ticker != second_ticker:
            cmd = "UPDATE pastTickers SET last_ticker = (?) WHERE owner_id = (?)"
            arg = (ticker, owner)      
        elif ticker != first_ticker and ticker != second_ticker and ticker != last_ticker:
            cmd = "UPDATE pastTickers SET first_ticker = (?), second_ticker = (?), last_ticker = (?) WHERE owner_id = (?)"
            arg = (second_ticker, last_ticker, ticker, owner)
        else:
            return
        self.conn.execute(cmd, arg)
        self.conn.commit()
        
        
    
    def getPastTickers(self, owner):
        try:
            ownerid = [x[0] for x in self.conn.execute("SELECT owner_id FROM pastTickers WHERE owner_id = (?)", (owner,))][0]
        except:
            return []
        cmd = "SELECT last_ticker, second_ticker, first_ticker FROM pastTickers WHERE owner_id = (?)"
        arg = (owner,)
        pasttickers = [x for x in self.conn.execute(cmd, arg)][0]
        return pasttickers