
import my_log as g_log
import my_normalize as g_normalize
import my_kmeans as g_kmeans
import my_groups as g_groups


def cluster( user_questions_arr, method, num_groups, min_df, max_df ):

    if ( ( num_groups is None ) and ( len( user_questions_arr ) < 3 ) ) or \
       ( ( num_groups is not None ) and ( len( user_questions_arr ) < num_groups ) ):
        groups_json = g_groups.defaultGroups( user_questions_arr )
        return groups_json, ""

    if( "semantic" == method ):
        groups_df, matrix, error_str = g_kmeans.cluster_semantic( user_questions_arr, num_groups )
        
    else:
        user_questions_arr_norm = g_normalize.normalizeLemmatizeTxt( user_questions_arr )
        groups_df, matrix, error_str = g_kmeans.cluster_bagOfWords( user_questions_arr_norm, num_groups, min_df, max_df )

    if error_str:
        return None, error_str
    
    error_str = g_groups.addGroupLabels( groups_df, 3 )
    if error_str:
        return None, error_str
    
    error_str = g_groups.addGroupScores( groups_df )
    if error_str:
        return None, error_str
    
    groups_json, error_str = g_groups.groupsJSON( groups_df )
    
    return groups_json, error_str





