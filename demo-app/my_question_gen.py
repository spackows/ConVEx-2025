
import my_log as g_log
import my_llm as g_llm
import my_job as g_job

from langchain_text_splitters import RecursiveCharacterTextSplitter
import json


def chunkContent( content ):
    try:
        text_splitter = RecursiveCharacterTextSplitter( 
            chunk_size=1000, 
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False
        )
        chunks_arr = text_splitter.split_text( content )
        return chunks_arr, ""
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_question_gen.chunkContent: " + error_str )
        return [], error_str

        
def genQuestions( job_id, content, model_id, prompt_parameters, prompt_template, b_debug=False ):
    model = None
    if( model_id is not None ):
        model, error_str = None if model_id is None else g_llm.txtGenModel( model_id, prompt_parameters )
        if error_str:
            g_job.updateStatus( job_id, "genQuestions error: " + error_str )
            return
    chunks_arr, error_str = chunkContent( content )
    if error_str:
        g_job.updateStatus( job_id, "genQuestions error: " + error_str )
        return
    try:
        g_job.updateStatus( job_id, "genQuestions info: Generating questions..." )
        q_arr = []
        for chunk_num in range( len( chunks_arr ) ):
            g_job.updateStatus( job_id, "genQuestions info: Chunk " + str( chunk_num + 1 ) + " of " + str( len( chunks_arr ) ) )
            for i in range( 5 ):
                g_job.updateStatus( job_id, "genQuestions info: Iteration " + str( i + 1 ) + " of 5" )
                output, gen_q_arr = g_llm.genQuestions( chunks_arr[ chunk_num ], model, prompt_template, b_debug )
                for question in gen_q_arr:
                    if question not in q_arr:
                        q_arr.append( question )
        g_job.updateStatus( job_id, "genQuestions info: Done!" )
        g_job.updateStatus( job_id, "generated_questions_arr begin:\n" + json.dumps( q_arr, indent=3 ) + "\ngenerated_questions_arr end" )
        return
    except Exception as e:
        error_str = str( e )
        g_job.updateStatus( job_id, "genQuestions error: " + error_str )
        return
