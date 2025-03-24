
function checkUserQuestions()
{
    var txt = document.getElementById( "user_questions_textarea" ).value.trim();

    var lines_arr = txt.split( /[\n\r]+/ );
    var line = "";
    var user_questions_arr = [];
    for( var i = 0; i < lines_arr.length; i++ )
    {
        line = lines_arr[i].replace( /[^a-z0-9\,\;\:\.\?\!\_\-]+/ig, " " ).replace( /\s+/g, " " ).trim();
        if( line.match( /\S/ ) )
        {
            user_questions_arr.push( line );
        }
    }
    
    if( user_questions_arr.length > 0 )
    {
        document.getElementById( "user_questions_textarea" ).style.borderColor = "lightgrey";
        document.getElementById( "user_questions_textarea" ).style.borderTop = "1px solid grey";
    }
    
    return user_questions_arr;
}


function getUserQuestions()
{
    var user_questions_arr = checkUserQuestions();
    
    if( user_questions_arr.length < 1 )
    {
        document.getElementById( "user_questions_textarea" ).style.borderColor = "red";
    }
    
    return user_questions_arr;
}


function checkContent()
{
    var txt = document.getElementById( "content_textarea" ).value;
    
    txt = txt.replace( /[^a-z0-9\,\;\:\.\?\!\_\-]+/ig, " " ).replace( /\s+/g, " " ).trim()
    
    if( txt.match( /\S/ ) )
    {
        document.getElementById( "content_textarea" ).style.borderColor = "lightgrey";
        document.getElementById( "content_textarea" ).style.borderTop = "1px solid grey";
    }
    
    return txt;
}


function getContent()
{
    var txt = checkContent();
    
    if( !txt.match( /\S/ ) )
    {
        document.getElementById( "content_textarea" ).style.borderColor = "red";
    }
    
    return txt;
}


function testContent()
{
    var user_questions_arr = getUserQuestions();
    
    var content = getContent();
    
    if( ( user_questions_arr.length < 1 ) || !content.match( /\S/ ) )
    {
        return;
    }

    document.getElementById( "comparison_main_div"          ).style.display = "none";
    document.getElementById( "overall_score_main_div"       ).style.display = "none";
    document.getElementById( "themes_main_div"              ).style.display = "none";
    document.getElementById( "generated_questions_main_div" ).style.display = "none";
    document.getElementById( "prompt_details_main_div"      ).style.display = "none";
    document.getElementById( "test_questions_spinner"       ).style.display = "inline-block";
    
    document.getElementById( "comparison_table"    ).innerHTML = "";
    document.getElementById( "overall_chart_div"   ).innerHTML = "";
    document.getElementById( "overall_score_label" ).innerHTML = "";
    removeThemeDivs();
    
    document.getElementById( "themes_spinner_all"       ).style.display = "none";
    document.getElementById( "themes_spinner_matched"   ).style.display = "none";
    document.getElementById( "themes_spinner_unmatched" ).style.display = "none";
    
    document.getElementById( "theme_type_radio_all"       ).checked = true;
    document.getElementById( "theme_type_radio_matched"   ).checked = false;
    document.getElementById( "theme_type_radio_unmatched" ).checked = false;
    
    _generateQuestions( content, function( gen_error_str, generated_questions_arr )
    {
        if( gen_error_str )
        {
            document.getElementById( "test_questions_spinner"   ).style.display = "none";
            alert( gen_error_str );
            return;
        }
        
        document.getElementById( "generated_questions_div" ).innerHTML = "<p>" + generated_questions_arr.join( "</p>\n<p>" ) + "</p>";
        
        _compareQuestions( user_questions_arr, generated_questions_arr, function( comp_error_str, comp_results_arr )
        {
            document.getElementById( "test_questions_spinner" ).style.display = "none";
            
            if( comp_error_str )
            {
                alert( comp_error_str );
                return;
            }
            
            populateResults( comp_results_arr );
            
            document.getElementById( "overall_score_main_div" ).style.display = "inline-block";
            
            document.getElementById( "comparison_main_div" ).style.display = "inline-block";
            setTableHeadingWidths();
            document.getElementById( "comparison_main_div" ).scrollIntoView( { behavior: "smooth" } );
            
            document.getElementById( "themes_spinner_all"       ).style.display = "block";
            document.getElementById( "themes_container_div_all" ).style.display = "block";
            document.getElementById( "themes_main_div"          ).style.display = "inline-block";

            _clusterQuestions( "all", function( cluster_error_str, groups_json )
            {
                document.getElementById( "themes_spinner_all" ).style.display = "none";
                
                if( cluster_error_str )
                {
                    alert( cluster_error_str );
                    return;
                }
                
                populateThemes( "all", groups_json );
                
            } );
        
        } );
        
    } );
}


function _generateQuestions( content, callback )
{
    var model_id = document.getElementById( "model_id_input" ).value;
    
    var prompt_parameters = null;
    try
    {
        var prompt_parameters_txt = document.getElementById( "prompt_parameters_textarea" ).value.trim();
        var prompt_parameters = JSON.parse( prompt_parameters_txt );
    }
    catch( e )
    {
        alert( "Warning: Parsing the specified prompt parameters failed.  Using the defaults." );
        prompt_parameters = null;
    }
    
    var prompt_template = document.getElementById( "prompt_template_textarea" ).value.trim() + "\n";
    
    $.ajax( { url         : "./generate-questions",
              type        : "POST",
              data        : JSON.stringify( { "content"  : content,
                                              "model_id" : model_id,
                                              "prompt_parameters" : prompt_parameters,
                                              "prompt_template"   : prompt_template } ),
              dataType    : "json",
              contentType : "application/json",
              complete : function( result )
                         {
                             var status_code = ( "status"     in result ) ? result["status"]     : "";
                             var status_text = ( "statusText" in result ) ? result["statusText"] : "";
                             
                             if( !( "responseJSON" in result ) || !result["responseJSON"] )
                             {
                                 var msg = "Testing content failed.\n\n";
                                 msg += ( status_code == "" ) ? "" : "\n\nStatus code: " + status_code;
                                 msg += ( status_text == "" ) ? "" : "\n\nStatus text: " + status_text;
                                 callback( msg, [] );
                                 return;
                             }
                             
                             if( ( "error_str" in result["responseJSON"] ) && result["responseJSON"]["error_str"] )
                             {
                                 var msg = "Testing content failed.\n\n" +
                                           "error_str: " + result["responseJSON"]["error_str"];
                                 callback( msg, [] );
                                 return;
                             };
                             
                             var generated_questions_arr = ( ( "questions_arr" in result["responseJSON"] ) && result["responseJSON"]["questions_arr"] ) ? result["responseJSON"]["questions_arr"] : [];
                             if( !generated_questions_arr || !Array.isArray( generated_questions_arr ) || ( generated_questions_arr.length < 1 ) )
                             {
                                 var msg = "Testing content failed.\n\n" +
                                           "No questions were generated by the large language model.";
                                 callback( msg, [] );
                                 return;
                             }
                             
                             callback( "", generated_questions_arr );
                             
                         }
                         
            } );

}


function showHideDetails( span_obj )
{
    if( span_obj.innerText.match( /view/i ) )
    {
        span_obj.innerHTML = "Hide details";
        document.getElementById( "generated_questions_main_div" ).style.display = "inline-block";
        document.getElementById( "prompt_details_main_div"      ).style.display = "inline-block";
        document.getElementById( "view_details_button_div" ).scrollIntoView( { behavior: "smooth" } );
        return;
    }
    
    span_obj.innerHTML = "View details";
    document.getElementById( "generated_questions_main_div" ).style.display = "none";
    document.getElementById( "prompt_details_main_div"      ).style.display = "none";
    return;
}

