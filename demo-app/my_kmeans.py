
import nltk
from nltk.cluster.kmeans import KMeansClusterer
from sklearn.cluster import KMeans
import re

import my_log as g_log
import my_matrix as g_matrix
import my_groups as g_groups


def cluster_semantic( user_questions_arr, num_clusters=None ):

    matrix, error_str = g_matrix.buildMatrix_semantic( user_questions_arr )
    if error_str:
        return None, None, error_str
    
    # https://www.nltk.org/api/nltk.cluster.kmeans.html
    #
    
    try:
        if num_clusters is None:
            num_clusters = 3
        clusterer = KMeansClusterer( num_clusters, distance=nltk.cluster.util.cosine_distance, repeats=5, avoid_empty_clusters=True )
        cluster_ids_arr = clusterer.cluster( matrix, assign_clusters=True )
        means_arr = clusterer.means()
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_kmeans.cluster_semantic: " + error_str )
        return None, None, error_str

    groups_df, error_str = g_groups.assembleKmeansGroups_semantic( user_questions_arr, matrix, cluster_ids_arr, means_arr )
    if error_str:
        return None, None, error_str
    
    return groups_df, matrix, error_str


def cluster_bagOfWords( user_questions_arr_norm, num_clusters=None, min_df=None, max_df=None ):

    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
    #
    
    matrix, error_str = g_matrix.buildMatrix_bagOfWords( user_questions_arr_norm, min_df, max_df )
    if error_str:
        return None, None, error_str
        
    try:
        if num_clusters is None:
            num_clusters = 3
        clusters = KMeans( n_clusters=num_clusters, n_init=5 ).fit( matrix )
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_kmeans.cluster_bagOfWords: " + error_str )
        return None, None, error_str
    
    groups_df, error_str = g_groups.assembleKmeansGroups_bagOfWords( user_questions_arr_norm, matrix, clusters )
    if error_str:
        return None, None, error_str
    
    return groups_df, matrix, error_str



