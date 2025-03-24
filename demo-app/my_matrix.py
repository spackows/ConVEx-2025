
import math
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.cluster.hierarchy import linkage

import my_log as g_log
import my_llm as g_llm

g_vectorizer = TfidfVectorizer( stop_words = "english" )


def buildMatrix_semantic( user_questions_arr ):
    # https://sbert.net
    #
    try:
        messages_arr = []
        for item in user_questions_arr:
            messages_arr.append( item["user_question"] )
        embeddings = g_llm.embed( messages_arr )
        return embeddings, None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_matrix.buildMatrix_semantic: " + error_str )
        return None, error_str
        

def buildMatrix_bagOfWords( user_questions_arr_norm, min_df_in=None, max_df_in=None ):
    # https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
    # "After ignoring terms that appear in more than 50% of the documents 
    # (as set by max_df=0.5) and terms that are not present in at least 
    # 5 documents (set by min_df=5), the resulting number of unique terms"
    #
    try:
        messages_arr = []
        for item in user_questions_arr_norm:
            messages_arr.append( item["user_question_norm"] )
        min_df = math.ceil( 0.1 * len( messages_arr ) ) if min_df_in is None else min_df_in
        max_df = 0.8 if max_df_in is None else max_df_in
        matrix = g_vectorizer.fit_transform( messages_arr )
        matrix = matrix.toarray()
        return matrix, None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_matrix.buildMatrix_bagOfWords: " + error_str )
        return None, error_str

