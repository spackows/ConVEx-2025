
g_log_file_name = "./static/log.txt"

def writeLog( str ):
    with open( g_log_file_name, "a") as myfile:
        myfile.write( str + "\n" )
    print( str )
    