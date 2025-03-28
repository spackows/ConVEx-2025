
function pollForGeneratedQuestions( job_id, counter, callback )
{
    if( counter > 30 )
    {
        var msg = "Job generating questions timed out";
        callback( msg, [] );
        return;
    }
    
    setTimeout( function()
    {
        _pollForStatus( job_id, function( error_str, status_txt )
        {
            if( error_str )
            {
                callback( error_str, [] );
                return;
            }
            
            if( status_txt.match( /genQuestions error/ ) )
            {
                var msg = getQuestionGenError( status_txt );
                callback( msg, [] );
                return;
            }
            
            if( status_txt.match( /generated_questions_arr begin/ ) && status_txt.match( /generated_questions_arr end/ ) )
            {
                try
                {
                    var generated_questions_arr = getQuestionsArr( status_txt );
                    callback( "", generated_questions_arr );
                }
                catch( e )
                {
                    var msg = "Parsing generated questions failed";
                    callback( msg, [] );
                    return;
                }
                
                return;
                    
            }
        
            pollForGeneratedQuestions( job_id, counter + 1, function( final_error_str, generated_questions_arr )
            {
                callback( final_error_str, generated_questions_arr );
                
            } );
        
        } );
        
    }, 5 * 1000 );
    
}


function _pollForStatus( job_id, callback )
{
    $.ajax( { url         : "./status",
              type        : "POST",
              data        : JSON.stringify( { "job_id" : job_id } ),
              dataType    : "json",
              contentType : "application/json",
              complete : function( result )
                         {
                             var status_code = ( "status"     in result ) ? result["status"]     : "";
                             var status_text = ( "statusText" in result ) ? result["statusText"] : "";
                             
                             if( !( "responseJSON" in result ) || !result["responseJSON"] )
                             {
                                 var msg = "A server-side job failed.\n\n";
                                 msg += ( status_code == "" ) ? "" : "\n\nStatus code: " + status_code;
                                 msg += ( status_text == "" ) ? "" : "\n\nStatus text: " + status_text;
                                 callback( msg, "" );
                                 return;
                             }
                             
                             if( ( "error_str" in result["responseJSON"] ) && result["responseJSON"]["error_str"] )
                             {
                                 var msg = "A server-side job failed.\n\n" +
                                           "error_str: " + result["responseJSON"]["error_str"];
                                 callback( msg, "" );
                                 return;
                             };
                             
                             var status_txt = ( ( "status_txt" in result["responseJSON"] ) && result["responseJSON"]["status_txt"] ) ? result["responseJSON"]["status_txt"] : "";
                             if( !status_txt )
                             {
                                 var msg = "A server-side job failed.";
                                 callback( msg, "" );
                                 return;
                             }
                             
                             updateStatusTxtDiv( status_txt );
                             
                             callback( "", status_txt );
                             
                         }
                         
            } );

}


function getQuestionGenError( status_txt )
{
    var matches_arr = status_txt.match( /genQuestions error: (.*?)\n/ );
    if( matches_arr.length > 1 )
    {
        return matches_arr[1];
    }
    
    return "Generating questions failed due to an unknown error";
}


function getQuestionsArr( status_txt )
{
    var generated_questions_txt = status_txt.replace( /^[\s\S]*generated_questions_arr begin:/, "" );
    generated_questions_txt = generated_questions_txt.replace( /generated_questions_arr end[\s\S]*$/, "" );
    
    var generated_questions_arr = JSON.parse( generated_questions_txt );
    
    return generated_questions_arr;
}


function pollForQuestionComparison( job_id, counter, callback )
{
    if( counter > 20 )
    {
        var msg = "Job comparing questions timed out";
        callback( msg, [] );
        return;
    }
    
    setTimeout( function()
    {
        _pollForStatus( job_id, function( error_str, status_txt )
        {
            if( error_str )
            {
                callback( error_str, [] );
                return;
            }
            
            if( status_txt.match( /compareQuestions error/ ) )
            {
                var msg = getQuestionCompError( status_txt );
                callback( msg, [] );
                return;
            }
            
            if( status_txt.match( /results_arr begin/ ) && status_txt.match( /results_arr end/ ) )
            {
                try
                {
                    var results_arr = getQuestionCompArr( status_txt );
                    callback( "", results_arr );
                }
                catch( e )
                {
                    var msg = "Parsing question comparison failed";
                    callback( msg, [] );
                    return;
                }
                
                return;
                    
            }
        
            pollForQuestionComparison( job_id, counter + 1, function( final_error_str, generated_questions_arr )
            {
                callback( final_error_str, generated_questions_arr );
                
            } );
        
        } );
        
    }, 5 * 1000 );
    
}


function getQuestionCompError( status_txt )
{
    var matches_arr = status_txt.match( /compareQuestions error: (.*?)\n/ );
    if( matches_arr.length > 1 )
    {
        return matches_arr[1];
    }
    
    return "Comparing questions failed due to an unknown error";
}


function getQuestionCompArr( status_txt )
{
    var results_txt = status_txt.replace( /^[\s\S]*results_arr begin:/, "" );
    results_txt = results_txt.replace( /results_arr end[\s\S]*$/, "" );
    
    var results_arr = JSON.parse( results_txt );
    
    return results_arr;
}


function updateStatusTxtDiv( status_txt )
{
    var matches_arr = status_txt.match( /genQuestions info: .*?\n|compareQuestions info: .*?\n/g );
    
    var txt = "";
    for( var i = 0; i < matches_arr.length; i++ )
    {
        txt += matches_arr[i].replace( /.*? info: /, "" ) + "<br/>";
    }
    
    document.getElementById( "status_txt_div" ).innerHTML = txt;
}


function _deleteJobFile( job_id )
{
    $.ajax( { url         : "./cleanup",
              type        : "POST",
              data        : JSON.stringify( { "job_id" : job_id } ),
              dataType    : "json",
              contentType : "application/json",
              complete : function( result )
                         {
                             // Don't care if it fails
                             
                         }
                         
            } );

}

