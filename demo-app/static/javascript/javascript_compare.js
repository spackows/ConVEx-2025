
function _compareQuestions( user_questions_arr, generated_questions_arr, callback )
{
    $.ajax( { url         : "./compare-questions",
              type        : "POST",
              data        : JSON.stringify( { "user_questions_arr" : user_questions_arr, "generated_questions_arr" : generated_questions_arr } ),
              dataType    : "json",
              contentType : "application/json",
              complete : function( result )
                         {
                             var status_code = ( "status"     in result ) ? result["status"]     : "";
                             var status_text = ( "statusText" in result ) ? result["statusText"] : "";
                             
                             if( !( "responseJSON" in result ) || !result["responseJSON"] )
                             {
                                 var msg = "Evaluating results failed.\n\n";
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
                             
                             var results_arr = ( ( "results_arr" in result["responseJSON"] ) && result["responseJSON"]["results_arr"] ) ? result["responseJSON"]["results_arr"] : [];
                             if( !results_arr || !Array.isArray( results_arr ) || ( results_arr.length < 1 ) )
                             {
                                 var msg = "Evaluating results failed.\n\n" +
                                           "No results were returned.";
                                 callback( msg, [] );
                                 return;
                             }
                             
                             callback( "", results_arr );
                             
                         }
                         
            } );

}


function populateResults( results_arr )
{
    var percent_correct = populateResultsTable( results_arr );
    
    sortTable();
    
    drawChart( "overall_chart_div", percent_correct );
}


function populateResultsTable( results_arr )
{
    //var check_txt = "";
    
    var num_correct = 0;
    var html = "";
    var answer_threshold = parseInt( document.getElementById( "answer_threshold_input" ).value );
    var user_question = "";
    var closest_generated_questions_arr = [];
    var closest_generated_question = "";
    var generated_questions_ul = "";
    var similarity_score = 0;
    var answered_yes_no = "";
    for( var i = 0; i < results_arr.length; i++ )
    {
        user_question = results_arr[i]["user_question"];
        closest_generated_questions_arr = results_arr[i]["closest_generated_questions_arr"];
        closest_generated_question = results_arr[i]["closest_generated_question"];
        for( var j = 0; j < closest_generated_questions_arr.length; j++ )
        {
            if( closest_generated_questions_arr[j] == closest_generated_question )
            {
                closest_generated_questions_arr[j] = "<b>" + closest_generated_questions_arr[j] + "</b>";
            }
        }
        
        generated_questions_ul = "<ul><li>" + closest_generated_questions_arr.join( "</li><li>" ) + "</li></ul>";
        
        similarity_score = Math.round( 100 * results_arr[i]["highest_score"] );
        
        if( similarity_score >= answer_threshold )
        {
            answered_yes_no = "<span class='green_check'>&#x2713;</span>";
            num_correct += 1;
        }
        else
        {
            answered_yes_no = "<span class='red_x'>&#x2717;</span>";
        }
        
        
        html += "<tr class='result_tr'>" +
                "<td text>" + user_question + "</td>" +
                "<td>" + generated_questions_ul + "</td>" +
                "<td style='min-width: 80px'>" + similarity_score + "</td>" +
                "<td style='border-right: none;'>" + answered_yes_no + "</td>" +
                "</tr>";
        
        //check_txt += similarity_score + "\t" + user_question + "\n";
    }
    
    //alert( check_txt );
    
    document.getElementById( "comparison_table" ).innerHTML = html;
    
    return Math.round( 100 * num_correct / results_arr.length );

}


function drawChart( chart_div_id, percent_correct ) 
{
    var num = parseInt( percent_correct );
    
    var chart_data = { datasets: [ { backgroundColor: [ "green", "white" ], data: [ num, 100 - num ] } ] };
    
    var chart_options = { tooltips: { enabled: false },
                          hover: { mode: null },
                          cutoutPercentage: 70
                        };

    new Chart( chart_div_id, { type    : "doughnut", 
                               data    : chart_data, 
                               options : chart_options } );

    var label_id = chart_div_id.replace( /_chart_div/, "_score_label" );
    
    document.getElementById( label_id ).innerHTML = percent_correct + "%";
    
}


function setTableHeadingWidths()
{
    var table = document.getElementById( "comparison_table" );
    var rows = ( table && table.children && ( table.children.length > 0 ) && table.children[0] ) ? table.children[0].children : [];
    
    if( rows.length < 1 )
    {
        return;
    }
    
    var heading_li_arr = document.getElementById( "comparison_table_titles_ul" ).children;
    
    var first_row = rows[0];
    var td_arr = first_row.children;
    for( var i = 0; i < ( td_arr.length - 1 ); i++ )
    {
        heading_li_arr[i].style.width = ( td_arr[i].clientWidth - 10 ).toString() + "px";
    }
}


function validateThresholdNumber()
{
    document.getElementById( "answer_threshold_input" ).value = document.getElementById( "answer_threshold_input" ).value.replace( /[^\d]/g, "" );
}


function setSlider( input_obj )
{
    document.getElementById( "answer_threshold_slider" ).value = input_obj.value;
}


var g_slider_value = 0;

function rememberValue( slider_obj )
{
    g_slider_value = slider_obj.value;
}


function isValueChanged( slider_obj )
{
    if( slider_obj.value == g_slider_value )
    {
        return;
    }
    
    document.getElementById( "answer_threshold_input" ).onchange();
}


function setThreshold( slider_obj )
{
    document.getElementById( "answer_threshold_input" ).value = slider_obj.value;
}


function updateResultsTable()
{
    var answer_threshold = document.getElementById( "answer_threshold_input" ).value;
    
    var rows_arr = document.getElementsByClassName( "result_tr" );
    var td_arr;
    var similarity_score = 0;
    var num_correct = 0;
    var answered_yes_no = "";
    for( var i = 0; i < rows_arr.length; i++ )
    {
        td_arr = rows_arr[i].children;
        
        similarity_score = parseInt( td_arr[2].innerText );
        
        if( similarity_score >= answer_threshold )
        {
            answered_yes_no = "<span class='green_check'>&#x2713;</span>";
            num_correct += 1;
        }
        else
        {
            answered_yes_no = "<span class='red_x'>&#x2717;</span>";
        }
        
        td_arr[3].innerHTML = answered_yes_no;
    }
    
    var percent_correct = Math.round( 100 * num_correct / rows_arr.length );
    
    drawChart( "overall_chart_div", percent_correct );
}


function switchChevron( chevron_obj )
{
    if( chevron_obj.className.match( /down/ ) )
    {
        chevron_obj.className = chevron_obj.className.replace( /down/, "up" );
        chevron_obj.title = "Sort highest to lowest";
    }
    else
    {
        chevron_obj.className = chevron_obj.className.replace( /up/, "down" );
        chevron_obj.title = "Sort lowest to highest";
    }

}


function sortTable()
{
    var chevron_obj = document.getElementById( "chevron" );
    
    var sort_order = "highest_to_lowest";
    
    if( chevron_obj.className.match( /up/ ) )
    {
        sort_order = "lowest_to_highest";
    }
    
    var rows_arr = Array.from( document.getElementsByClassName( "result_tr" ) );
    
    rows_arr.sort( function( x, y )
    {
        x_score = parseInt( x.children[2].innerText );
        y_score = parseInt( y.children[2].innerText );
        
        if( x_score < y_score )
        {
            return ( "highest_to_lowest" == sort_order ) ? 1 : -1;
        }
        
        if( x_score > y_score )
        {
            return ( "highest_to_lowest" == sort_order ) ? -1 : 1;
        }
      
        return 0;
    
    } );
    
    var tr;
    var tbl = document.getElementById( "comparison_table" ).children[0]; // tbody
    for( var i = 0; i < rows_arr.length; i++ )
    {
        tr = tbl.removeChild( rows_arr[i] );
        tbl.appendChild( tr );
    }
    
}



