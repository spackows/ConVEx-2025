
import scipy
import pandas as pd
import numpy as np
import math
from sklearn.feature_extraction.text import TfidfVectorizer

import my_log as g_log
import my_normalize as g_normalize


g_vectorizer = TfidfVectorizer( stop_words = "english" )


def assembleKmeansGroups_semantic( user_questions_arr, matrix, cluster_ids_arr, means_arr ):
    results_arr = []
    try:
        distances_arr = []
        for i in range( len( cluster_ids_arr ) ):
            cluster_id = cluster_ids_arr[i]
            vector = matrix[i,:]
            mean = means_arr[ cluster_id ]
            distance = scipy.spatial.distance.cosine( vector, mean )
            distances_arr.append( distance )
        spread = np.max(distances_arr) - np.min(distances_arr)
        distances_arr_norm = [1]*len(distances_arr) if ( 0 == spread ) else list( ( (distances_arr - np.min(distances_arr)) / spread ).round(3) )
        groups_json = {}
        for i in range( len( user_questions_arr ) ):
            highest_score = user_questions_arr[i]["highest_score"]
            user_question = user_questions_arr[i]["user_question"]
            cluster_id = str( cluster_ids_arr[i] )
            distance = distances_arr_norm[i]
            results_arr.append( { "group_id" : cluster_id, "distance" : distance, "highest_score" : highest_score, "user_question" : user_question } )
        results_df = pd.DataFrame( results_arr )    
        return results_df, None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_groups.assembleKmeansGroups_semantic: " + error_str )
        return None, error_str


def assembleKmeansGroups_bagOfWords( user_questions_arr_norm, matrix, clusters ):
    results_arr = []
    try:
        cluster_ids_arr = list( clusters.labels_ )
        distance_matrix = clusters.transform( matrix )**2
        distances_arr = distance_matrix.sum( axis=1 )
        spread = np.max(distances_arr) - np.min(distances_arr)
        distances_arr_norm = [1]*len(distances_arr) if ( 0 == spread ) else list( ( (distances_arr - np.min(distances_arr)) / spread ).round(3) )
        for i in range( len( user_questions_arr_norm ) ):
            highest_score = user_questions_arr_norm[i]["highest_score"]
            user_question = user_questions_arr_norm[i]["user_question"]
            cluster_id = str( cluster_ids_arr[i] )
            distance = distances_arr_norm[i]
            results_arr.append( { "group_id" : cluster_id, "distance" : distance, "highest_score" : highest_score, "user_question" : user_question } )
        results_df = pd.DataFrame( results_arr )    
        return results_df, None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_groups.assembleKmeansGroups_bagOfWords: " + error_str )
        return None, error_str


def addGroupScores( groups_df ):
    if groups_df is None:
        return
    try:
        groups_df["group_distance"] = -1.0
        group_ids_arr = groups_df["group_id"].unique()
        for group_id in group_ids_arr:
            group_distances = sorted( list( groups_df[ ( groups_df.group_id == group_id ) ]["distance"] ) )
            best_distances = group_distances[ : math.ceil( len(group_distances)/2 ) ]
            group_distance = 1 if ( len( best_distances ) < 1 ) else round( sum( best_distances ) / len( best_distances ), 3 )
            groups_df.loc[ groups_df.group_id == group_id, "group_distance" ] = group_distance
        #groups_df.sort_values( [ "group_distance", "distance" ], ascending=[ True, True ], inplace=True )
        return None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_groups.addGroupScores: " + error_str )
        return error_str


def groupLabel( txt_arr, n ):
    matrix = g_vectorizer.fit_transform( txt_arr ).todense()
    df = pd.DataFrame( matrix, columns=g_vectorizer.get_feature_names_out() )
    series = df.sum().sort_values( ascending=False )
    return " | ".join( list( series.keys() )[0:n] )
    
    
def addGroupLabels( groups_df, n ):
    if groups_df is None:
        return
    try:
        groups_df["group_label"] = ""
        group_ids_arr = groups_df["group_id"].unique()
        for group_id in group_ids_arr:
            questions_arr = list( groups_df[ ( groups_df.group_id == group_id ) ]["user_question"] )
            questions_arr = g_normalize.normalizeTxtForLabel( questions_arr )
            group_label = groupLabel( questions_arr, n )
            groups_df.loc[ groups_df.group_id == group_id, "group_label" ] = group_label
        return None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_groups.addGroupLabels: " + error_str )
        return error_str


def groupsJSON( groups_df ):
    if ( groups_df is None ) or ( groups_df.shape[0] < 1 ):
        return {}, ""
    try:
        groups_json = {}
        group_ids_arr = list( groups_df["group_id"].unique() )
        for group_id in group_ids_arr:
            group_df = groups_df[ ( groups_df.group_id == group_id ) ]
            groups_json[ str( group_id ) ] = {}
            groups_json[ str( group_id ) ]["group_label"] = list( group_df["group_label"] )[0]
            groups_json[ str( group_id ) ]["group_distance"] = list( group_df["group_distance"] )[0] if "group_distance" in group_df else -1
            groups_json[ str( group_id ) ]["members_arr"] = []
            distances = list( group_df["distance"] ) if "distance" in group_df else [ -1 ] * group_df.shape[0]
            scores_arr = list( group_df["highest_score"] )
            user_questions_arr = list( group_df["user_question"] )
            for i in range( len( user_questions_arr ) ):
                groups_json[ str( group_id ) ]["members_arr"].append( { "distance" : distances[i], "highest_score" : scores_arr[i], "user_question" : user_questions_arr[i] } )
            groups_json[ str( group_id ) ]["members_arr"].sort( key=lambda x: x["distance"] )
        return groups_json, None
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_groups.groupsJSON: " + error_str )
        return None, error_str


def defaultGroups( user_questions_arr ):
    groups_json = { "0": { "group_distance": 1,
                           "group_label": "(Not enough questions to cluster )",
                           "members_arr": [] } }
    for item in user_questions_arr:
        groups_json["0"]["members_arr"].append( { "distance": 1,
                                                  "highest_score" : item["highest_score"],
                                                  "user_question" : item["user_question"] } )
    return groups_json
