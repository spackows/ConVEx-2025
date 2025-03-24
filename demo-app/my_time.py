
from datetime import datetime


def getTS():
    now = datetime.now()
    ts = datetime.timestamp( now )
    return round( ts * 1000 )
    
def myGetLongDateStrUTC( ts ):
    dt_object = datetime.utcfromtimestamp( round( ts / 1000 ) )
    date_str = dt_object.strftime( "%Y-%m-%d %H:%M:%S" )
    return date_str


def getTSStr():
    ts = getTS()
    ts_str = myGetLongDateStrUTC( ts )
    return "[" + ts_str + "]"

