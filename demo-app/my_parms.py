
import my_log as g_log

import json

def getParms( request, parm_names_arr ):
    parms_json = None
    try:
        parms_json = request.get_json()
        #if parms_json:
        #    g_log.writeLog( "[server] getParms parms_json:\n" + json.dumps( parms_json, indent=3 ) )
    except Exception as e:
        g_log.writeLog( "[server] getParms parms not JSON" )
    #if request.values:
    #    g_log.writeLog( "[server] getParms request.values:\n" + json.dumps( request.values, indent=3 ) )
    parm_vals = {}
    error_str = None
    try:
        for parm_name in parm_names_arr:
            if parms_json:
                if parm_name in parms_json:
                    parm_vals[ parm_name ] = parms_json[ parm_name ]
            elif request.values.get( parm_name ):
                parm_vals[ parm_name ] = request.values.get( parm_name )
            elif request.files.get( parm_name ):
                parm_vals[ parm_name ] = request.files.get( parm_name )
        if not parm_vals:
            error_str = "No parameters were specified"
        return parm_vals, error_str
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getParms: " + error_str )
        return parm_vals, error_str


def getcontent( parm_vals ):
    content = ""
    error_str = ""
    try:
        if "content" not in parm_vals:
            error_str = "Missing parameter: 'content' was not specified"
            return content, error_str
        content = parm_vals["content"]
        return content, error_str
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getcontent: " + error_str )
        return content, error_str


def getuserquestions( parm_vals ):
    user_questions_arr = []
    error_str = ""
    try:
        if "user_questions_arr" not in parm_vals:
            error_str = "Missing parameter: 'user_questions_arr' was not specified"
            return user_questions_arr, error_str
        user_questions_arr = parm_vals["user_questions_arr"]
        return user_questions_arr, error_str
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getuserquestions: " + error_str )
        return user_questions_arr, error_str


def getgeneratedquestions( parm_vals ):
    generated_questions_arr = []
    error_str = ""
    try:
        if "generated_questions_arr" not in parm_vals:
            error_str = "Missing parameter: 'generated_questions_arr' was not specified"
            return generated_questions_arr, error_str
        generated_questions_arr = parm_vals["generated_questions_arr"]
        return generated_questions_arr, error_str
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getgeneratedquestions: " + error_str )
        return generated_questions_arr, error_str


def getmodelid( parm_vals ):
    try:
        if "model_id" in parm_vals:
            return parm_vals["model_id"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getmodelid: " + error_str )
        return None


def getpromptparams( parm_vals ):
    try:
        if "prompt_parameters" in parm_vals:
            return parm_vals["prompt_parameters"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getpromptparams: " + error_str )
        return None


def getprompttemplate( parm_vals ):
    try:
        if "prompt_template" in parm_vals:
            return parm_vals["prompt_template"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getprompttemplate: " + error_str )
        return None


def getdebug( parm_vals ):
    try:
        if "debug" in parm_vals:
            if re.match( r"1|true", str( parm_vals["debug"] ), re.IGNORECASE ):
                return True
            return False
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getdebug: " + error_str )
        return False


def getmethod( parm_vals ):
    try:
        if "method" in parm_vals:
            return parm_vals["method"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getmethod: " + error_str )
        return None


def getnumgroups( parm_vals ):
    try:
        if "num_groups" in parm_vals:
            return parm_vals["num_groups"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getnumgroups: " + error_str )
        return None


def getmindocs( parm_vals ):
    try:
        if "min_docs" in parm_vals:
            return parm_vals["min_docs"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getmindocs: " + error_str )
        return None


def getmaxpercent( parm_vals ):
    try:
        if "max_percent" in parm_vals:
            return parm_vals["max_percent"]
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getmaxpercent: " + error_str )
        return None


def getjobid( parm_vals ):
    job_id = ""
    error_str = ""
    try:
        if "job_id" not in parm_vals:
            error_str = "Missing parameter: 'job_id' was not specified"
            return job_id, error_str
        job_id = parm_vals["job_id"]
        return job_id, error_str
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "[server] getjobid: " + error_str )
        return job_id, error_str

