
import nltk
nltk.download( "punkt_tab" )
nltk.download( "averaged_perceptron_tagger_eng" )
nltk.download( "stopwords" )
nltk.download( "wordnet" )

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

import re

import my_log as g_log


g_lemmatizer = WordNetLemmatizer()
g_stopwords_arr = stopwords.words( "english" )


def cleanTextPiece( txt_in ):
    txt = txt_in.lower()
    txt = re.sub( r"[^a-z0-9 ]", " ", txt )
    txt = re.sub( r"\s+", " ", txt )
    txt = txt.strip()
    return txt
        

def customTokenize( txt_in ):
    tokens_arr = []
    try:
        txt = cleanTextPiece( txt_in )
        tokens_arr = word_tokenize( txt )
        return tokens_arr, ""
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_normalize.customTokenize:\n" + \
                        "txt_in: " + txt_in + "\n" + \
                        "txt: " + txt + "\n" + \
                        "tokens_arr:\n" + json.dumps( tokens_arr, indent=3 ) + "\n" + \
                        "error_str: " + error_str )
        return [], error_str


def getWordnetPOS( tag ):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def customLemmatize( tokens_arr_in ):
    try:
        pos_dict = nltk.pos_tag( tokens_arr_in )
        tokens_arr = []
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_normalize.customLemmatize:\n" + \
                        "tokens_arr_in:\n" + json.dumps( tokens_arr_in, indent=3 ) + "\n" + \
                        "error_str: " + error_str )
        return [], error_str
    for index, tag in enumerate( pos_dict ):
        try:
            token = tokens_arr_in[index]
            if( token in g_stopwords_arr ):
                continue
            pos_info = tag[1]
            lemma = g_lemmatizer.lemmatize( token, getWordnetPOS( pos_info ) )
            tokens_arr.append( lemma )
        except Exception as e:
            error_str = str( e )
            g_log.writeLog( "my_normalize.customLemmatize:\n" + \
                            "tokens_arr_in:\n" + json.dumps( tokens_arr_in, indent=3 ) + "\n" + \
                            "pos_dict:\n" + json.dumps( pos_dict, indent=3 ) + "\n" + \
                            "index: " + str( index ) + "\n" + \
                            "tag:\n" + json.dumps( tag, indent=3 ) + "\n" + \
                            "tokens_arr:\n" + json.dumps( tokens_arr, indent=3 ) + "\n" + \
                            "error_str: " + error_str )
            return [], error_str
    return tokens_arr, ""


def normalizeLemmatizeTxt( user_questions_arr ):
    user_questions_arr_norm = []
    for item in user_questions_arr:
        highest_score = item["highest_score"]
        user_question = item["user_question"]
        tokens_arr, error_str = customTokenize( user_question )
        if error_str:
            continue
        tokens_arr, error_str = customLemmatize( tokens_arr )
        if error_str:
            continue
        user_questions_arr_norm.append( { "highest_score" : highest_score,
                                          "user_question" : user_question, 
                                          "user_question_norm" : " ".join( tokens_arr ) } )
    return user_questions_arr_norm


def normalizeTxtForLabel( user_questions_arr ):
    user_questions_arr_norm = []
    for user_question in user_questions_arr:
        tokens_arr, error_str = customTokenize( user_question )
        if not error_str:
            tokens_arr, error_str = customLemmatize( tokens_arr )
        user_question_norm = user_question if error_str else " ".join( tokens_arr )
        user_questions_arr_norm.append( user_question_norm )
    return user_questions_arr_norm


