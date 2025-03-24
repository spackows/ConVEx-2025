
from flask import Flask, request
import os

import my_log as g_log
import my_parms as g_parms
import my_question_gen as g_gen
import my_question_comp as g_comp
import my_cluster as g_cluster


app = Flask( __name__, static_url_path="" )

port = int( os.getenv( 'PORT', 8080 ) )


@app.route( "/generate-questions", methods = ["POST"] )
def generateQuestions():
    g_log.writeLog( "[server] /generate-questions" )
    
    parms, error_str = g_parms.getParms( request, [ "apikey", "content", "model_id", "prompt_parameters", "prompt_template", "debug" ] )
    if error_str:
        return { "error_str" : error_str }, 200
    
    content, error_str = g_parms.getcontent( parms )
    if error_str:
        return { "error_str" : error_str }, 200
    
    model_id     = g_parms.getmodelid( parms )
    prompt_parms = g_parms.getpromptparams( parms )
    prompt_tmplt = g_parms.getprompttemplate( parms )
    b_debug      = g_parms.getdebug( parms )
    
    questions_arr, error_str = g_gen.genQuestions( content, model_id, prompt_parms, prompt_tmplt, b_debug )
    if error_str:
        return { "error_str" : error_str }, 200
    
    return { "questions_arr" : questions_arr }


@app.route( "/compare-questions", methods = ["POST"] )
def compareQuestions():
    g_log.writeLog( "[server] /compare-questions" )
    
    parms, error_str = g_parms.getParms( request, [ "apikey", "user_questions_arr", "generated_questions_arr" ] )
    if error_str:
        return { "error_str" : error_str }, 200
    
    user_questions_arr, error_str = g_parms.getuserquestions( parms )
    if error_str:
        return { "error_str" : error_str }, 200
    
    generated_questions_arr, error_str = g_parms.getgeneratedquestions( parms )
    if error_str:
        return { "error_str" : error_str }, 200
    
    results_arr, error_str = g_comp.compareQuestions( user_questions_arr, generated_questions_arr )
    if error_str:
        return { "error_str" : error_str }, 200
    
    return { "results_arr" : results_arr }


# expected user_questions_arr like:
# [
#    {
#       "user_question" : "what is the color of the moon?",
#       "highest_score" : 33
#    },
#    ...
# ]
#
@app.route( "/cluster-questions", methods = ["POST"] )
def clusterQuestions():
    g_log.writeLog( "[server] /cluster-questions" )
    
    parms, error_str = g_parms.getParms( request, [ "apikey", "user_questions_arr", "method", "num_groups", "min_docs", "max_percent" ] )
    if error_str:
        return { "error_str" : error_str }, 200
    
    user_questions_arr, error_str = g_parms.getuserquestions( parms )
    if error_str:
        return { "error_str" : error_str }, 200
    
    method      = g_parms.getmethod( parms )
    num_groups  = g_parms.getnumgroups( parms )
    min_docs    = g_parms.getmindocs( parms )
    max_percent = g_parms.getmaxpercent( parms )
    
    groups_json, error_str = g_cluster.cluster( user_questions_arr, method, num_groups, min_docs, max_percent )
    
    return { "groups_json" : groups_json, "error_str" : error_str }, 200


@app.route( "/health", methods = ["GET","POST"] )
def health():
    g_log.writeLog( "[server] /health" )
    return "Success"


@app.route( "/logs" )
def logs():
    return app.send_static_file( "log.txt" )


@app.route( "/" )
def root():
    return app.send_static_file( "index.html" )


if __name__ == '__main__':
    app.run( host='0.0.0.0', port=port, debug=True )
