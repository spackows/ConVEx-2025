
import random
import string
import _thread as thread
import os
import re

import my_time as g_time
import my_log as g_log
import my_question_gen as g_gen
import my_question_comp as g_comp


def genJobID():
    try:
        random_txt = "".join( random.choice( string.ascii_letters + string.digits ) for i in range(9) )
        ts = g_time.getTS()
        job_id = str( ts ) + "_" + random_txt
        file_name = "./static/jobs/" + job_id + ".txt"
        with open( file_name, "w" ) as f:
            f.write( "start\n" )
        return job_id
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[my_job] genJobID: " + error_str )
        return ""
    

def runQuestionGenJob( content, model_id, prompt_parms, prompt_tmplt, b_debug ):
    job_id = genJobID()
    if not job_id:
        return "", "Generating job ID failed"
    try:
        thread.start_new_thread( g_gen.genQuestions, ( job_id, content, model_id, prompt_parms, prompt_tmplt, b_debug ) )
        return job_id, ""
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[my_job] runQuestionGenJob: " + error_str )
        return "", error_str


def runQuestionCompJob( job_id, user_questions_arr, generated_questions_arr ):
    try:
        thread.start_new_thread( g_comp.compareQuestions, ( job_id, user_questions_arr, generated_questions_arr ) )
        return ""
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[my_job] runQuestionCompJob: " + error_str )
        return error_str


def updateStatus( job_id, details ):
    try:
        if re.match( r" error: ", details ):
            g_log.writeLog( "[" + job_id + "]\n" + details )
        file_name = "./static/jobs/" + job_id + ".txt"
        with open( file_name, "a" ) as f:
            f.write( details + "\n" )
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[my_job] updateStatus: " + "[" + job_id + "] " + error_str )


def getStatus( job_id ):
    try:
        file_name = "./static/jobs/" + job_id + ".txt"
        with open( file_name, "r" ) as f:
            contents = f.read()
        return { "status_txt" : contents }
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[my_job] getStatus: " + "[" + job_id + "] " + error_str )
        return { "error_str" : error_str }


def deleteJobFile( job_id ):
    try:
        file_name = "./static/jobs/" + job_id + ".txt"
        os.remove( file_name )
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[my_job] deleteJobFile: " + "[" + job_id + "] " + error_str )
        return { "error_str" : error_str }


