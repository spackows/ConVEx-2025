
import my_log as g_log
import my_llm as g_llm

from langchain_text_splitters import RecursiveCharacterTextSplitter


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

        
def genQuestions( content, model_id, prompt_parameters, prompt_template, b_debug=False ):
    model = None
    if( model_id is not None ):
        model, error_str = None if model_id is None else g_llm.txtGenModel( model_id, prompt_parameters )
        if error_str:
            return [], error_str
    chunks_arr, error_str = chunkContent( content )
    if error_str:
        return [], error_str
    try:
        q_arr = []
        for chunk_num in range( len( chunks_arr ) ):
            g_log.writeLog( str( chunk_num ) + " of " + str( len( chunks_arr ) ) )
            for i in range( 5 ):
                g_log.writeLog( "Iteration " + str( i ) )
                output, gen_q_arr = g_llm.genQuestions( chunks_arr[ chunk_num ], model, prompt_template, b_debug )
                for question in gen_q_arr:
                    if question not in q_arr:
                        q_arr.append( question )
        return q_arr, ""
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_question_gen.genQuestions: " + error_str )
        return [], error_str