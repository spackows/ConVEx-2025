
function _clusterQuestions( cluster_type, callback )
{
    var user_questions_arr = getQuestionsFromTable( cluster_type );
    
    $.ajax( { url         : "./cluster-questions",
              type        : "POST",
              data        : JSON.stringify( { "user_questions_arr" : user_questions_arr } ),
              dataType    : "json",
              contentType : "application/json",
              complete : function( result )
                         {
                             var status_code = ( "status"     in result ) ? result["status"]     : "";
                             var status_text = ( "statusText" in result ) ? result["statusText"] : "";
                             
                             if( !( "responseJSON" in result ) || !result["responseJSON"] )
                             {
                                 var msg = "Clustering results failed.\n\n";
                                 msg += ( status_code == "" ) ? "" : "\n\nStatus code: " + status_code;
                                 msg += ( status_text == "" ) ? "" : "\n\nStatus text: " + status_text;
                                 callback( msg, {} );
                                 return;
                             }
                             
                             if( ( "error_str" in result["responseJSON"] ) && result["responseJSON"]["error_str"] )
                             {
                                 var msg = "Clustering results failed.\n\n" +
                                           "error_str: " + result["responseJSON"]["error_str"];
                                 callback( msg, {} );
                                 return;
                             };
                             
                             var groups_json = ( ( "groups_json" in result["responseJSON"] ) && result["responseJSON"]["groups_json"] ) ? result["responseJSON"]["groups_json"] : [];
                             if( !groups_json )
                             {
                                 var msg = "Clustering results failed.\n\n" +
                                           "No results were returned.";
                                 callback( msg, {} );
                                 return;
                             }
                             
                             callback( "", groups_json );
                             
                         }
                         
            } );

}


function getQuestionsFromTable( cluster_type )
{
    var user_questions_arr = [];
    
    var rows_arr = document.getElementsByClassName( "result_tr" );
    var td_arr;
    var user_question = "";
    var highest_score = 0;
    var matched_html = "";
    for( var i = 0; i < rows_arr.length; i++ )
    {
        td_arr = rows_arr[i].children;
        
        user_question = td_arr[0].innerText;
        
        highest_score = parseInt( td_arr[2].innerText );
        
        matched_html = td_arr[3].innerHTML;
        
        if( ( "all" == cluster_type ) ||
            ( ( "matched"   == cluster_type ) && matched_html.match( /green_check/ ) ) ||
            ( ( "unmatched" == cluster_type ) && matched_html.match( /red_x/ ) ) )
        {
            user_questions_arr.push( { "user_question" : user_question, "highest_score" : highest_score } );
        }
    }
    
    return user_questions_arr;

}


function populateThemes( cluster_type, groups_json )
{
    var answer_threshold = parseInt( document.getElementById( "answer_threshold_input" ).value );
    
    var group_ids_arr = Object.keys( groups_json );
    
    if( group_ids_arr.length < 1 )
    {
        var div = document.createElement( "div" );
        div.className = "theme_div";
        div.id = "theme_div_0";
        div.style.border = "none";
        div.innerHTML = "<i style='margin: 60px 0px 100px 40px;'>No clusters</i>";
        
        document.getElementById( "themes_container_div_" + cluster_type ).appendChild( div );
        
        return;
    }
    
    group_ids_arr.sort( function( x, y )
    {
        if( groups_json[ x ]["members_arr"].length < groups_json[ y ]["members_arr"].length )
        {
            return 1;
        }
        
        if( groups_json[ x ]["members_arr"].length > groups_json[ y ]["members_arr"].length )
        {
            return -1;
        }
        
        return 0;
        
    } );

    var group_label = "";
    var members_arr = [];
    var label_html = "";
    var ul_html = "";
    var num_matched = 0;
    var similarity_score = 0;
    var percent_correct = 0;
    var score_html = "";
    var div;
    for( var i = 0; i < group_ids_arr.length; i++ )
    {
        group_label = groups_json[ group_ids_arr[i] ]["group_label"];
        members_arr = groups_json[ group_ids_arr[i] ]["members_arr"];
        
        label_html = "<div class='theme_label'>" + group_label + "</div>";
        
        ul_html = "<div class='theme_ul_container'>" +
                  "<ul>";
        
        num_matched = 0;
        for( var j = 0; j < members_arr.length; j++ )
        {
            similarity_score = members_arr[j]["highest_score"];
            if( similarity_score >= answer_threshold )
            {
                num_matched += 1;
            }
            
            ul_html += "<li>" + members_arr[j]["user_question"] + " (" + similarity_score + ")</li>";
            
        }
        
        ul_html += "</ul>" +
                   "</div>";
                   
        percent_correct = ( members_arr.length < 1 ) ? 0 : Math.round( 100 * num_matched / members_arr.length );
        
        score_html = "<div class='score_label'>" + percent_correct + "%</div>";
        
        div = document.createElement( "div" );
        div.className = "theme_div";
        div.id = "theme_div_" + i.toString();
        div.innerHTML = score_html +
                        label_html +
                        ul_html;
        
        document.getElementById( "themes_container_div_" + cluster_type ).appendChild( div );
    }
}


function removeThemeDivs()
{
    var theme_divs_arr = document.getElementsByClassName( "theme_div" );
    while( theme_divs_arr.length > 0 )
    {
        theme_divs_arr[0].remove();
    }
}


function showClusters()
{
    var cluster_type = getClusterType();
    if( !cluster_type )
    {
        return;
    }
    
    if( document.getElementById( "themes_container_div_" + cluster_type ).children.length < 2 )
    {
        document.getElementById( "themes_spinner_" + cluster_type ).style.display = "block";
        
        _clusterQuestions( cluster_type, function( cluster_error_str, groups_json )
        {
            document.getElementById( "themes_spinner_" + cluster_type ).style.display = "none";
            
            if( cluster_error_str )
            {
                alert( cluster_error_str );
                return;
            }
            
            populateThemes( cluster_type, groups_json );
            
        } );
    }
    
    var container_divs_arr = document.getElementsByClassName( "themes_container_div" );
    for( var i = 0; i < container_divs_arr.length; i++ )
    {
        if( container_divs_arr[i].id.replace( /^themes_container_div_/, "" ) != cluster_type )
        {
            container_divs_arr[i].style.display = "none";
        }
    }
    
    document.getElementById( "themes_container_div_" + cluster_type ).style.display = "block";
    
}


function getClusterType()
{
    var radio_buttons_arr = document.getElementsByClassName( "theme_radio" );
    var cluster_type = "";
    for( var i = 0; i < radio_buttons_arr.length; i++ )
    {
        if( radio_buttons_arr[i].checked )
        {
            cluster_type = radio_buttons_arr[i].id.replace( /^theme_type_radio_/, "" );
        }
    }
    
    return cluster_type;
}


function updateClusters()
{
    removeThemeDivs();
    showClusters();
}


