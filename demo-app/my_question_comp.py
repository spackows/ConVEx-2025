
import my_log as g_log
import my_llm as g_llm
import my_job as g_job

import json
import time
import subprocess
import sys
subprocess.check_call( [ sys.executable, "-m", "pip", "install", "sentence-transformers" ] )

from sentence_transformers import util
import numpy as np


def closestGeneratedQuestions( user_question, generated_questions_arr, num=3 ):
    scores_arr = g_llm.rerank( user_question, generated_questions_arr ) 
    scores_arr.sort( key=lambda x: x["score"], reverse=True )
    closest_generated_questions = []
    for score_obj in scores_arr[0:num]:
        index = score_obj["index"]
        generated_question = generated_questions_arr[ index ]
        closest_generated_questions.append( generated_question )
    return closest_generated_questions


def similarityScore( txt, txt_arr ):
    txt1_embeddings = g_llm.embed( [ txt ] )
    txt2_embeddings = g_llm.embed( txt_arr )
    cosine_scores = util.cos_sim( txt1_embeddings, txt2_embeddings ).tolist()[0]
    index_max = np.argmax( cosine_scores )
    highest_score = round( float( cosine_scores[ index_max ] ), 3 )
    closest_match = txt_arr[ index_max ]
    return highest_score, closest_match


def compareQuestions( job_id, user_questions_arr, generated_questions_arr ):
    try:
        g_job.updateStatus( job_id, "compareQuestions info: Comparing questions..." )
        counter = 0
        results_arr = []
        for user_question in user_questions_arr:
            counter += 1
            if( 0 == counter % 3 ):
                # https://ibm.github.io/watsonx-ai-python-sdk/rate_limit.html
                # Can only make 8 calls per second
                # This kludge will usually avoid being throttled, even 
                # with multiple team members making calls at once
                g_job.updateStatus( job_id, "compareQuestions info: Question " + str( counter ) + "/" + str( len( user_questions_arr ) ) )
                time.sleep( 1 )
            closest_generated_questions_arr = closestGeneratedQuestions( user_question, generated_questions_arr )
            highest_score, closest_question = similarityScore( user_question, closest_generated_questions_arr )
            results_arr.append( { "user_question" : user_question,
                                  "closest_generated_question" : closest_question,
                                  "highest_score" : highest_score,
                                  "closest_generated_questions_arr" : closest_generated_questions_arr } )
        g_job.updateStatus( job_id, "compareQuestions info: Done!" )
        g_job.updateStatus( job_id, "results_arr begin:\n" + json.dumps( results_arr, indent=3 ) + "\nresults_arr end" )
        return
    except Exception as e:
        error_str = str( e )
        g_job.updateStatus( job_id, "compareQuestions error: " + error_str )
        return
