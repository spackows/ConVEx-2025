
import my_log as g_log

from ibm_watsonx_ai import Credentials, APIClient
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models import Rerank
from ibm_watsonx_ai.foundation_models import Embeddings

import json
import re
import os


g_cloud_apikey    = os.getenv( "CLOUDAPIKEY" )
g_wml_service_url = os.getenv( "WMLURL" )
g_project_id      = os.getenv( "WXPROJECTID" )

# https://ibm.github.io/watsonx-ai-python-sdk/base.html#credentials
g_credentials = Credentials(
   api_key = g_cloud_apikey, 
   url = g_wml_service_url
)

# https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-model-parameters.html?context=wx&audience=wdp
g_prompt_parameters_gen_questions = {
    "decoding_method" : "sample",
    "temperature"     : 0.2,
    "top_p"           : 1,
    "top_k"           : 10,
    "min_new_tokens"  : 0,
    "max_new_tokens"  : 200,
    "stop_sequences"  : [ "\n\n" ]
}

# https://ibm.github.io/watsonx-ai-python-sdk/fm_model_inference.html#ibm_watsonx_ai.foundation_models.inference.ModelInference
g_model_gen_questions = ModelInference( 
    model_id    = "meta-llama/llama-3-3-70b-instruct", 
    params      = g_prompt_parameters_gen_questions, 
    credentials = g_credentials, 
    project_id  = g_project_id 
)

# https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-prompt-tips.html?context=wx&audience=wdp
g_template_gen_questions = """Generate 10 unique questions that are answered by the given article.  
Generate questions for as many facts as possible.  
Only generate questions for which the facts of the answer are in the article.

Article
----
## Growing tomatoes in pots 
Most tomato plants do well in containers. 
Determinate varieties don't grow as large as indeterminate varieties. 
For anything other than compact determinate varieties, use a 5 gallon container at a minimum. 
----

Ten (10) unique questions answered by the article:
1. Can you grow tomatoes in containers?
2. Do tomato plants do well in containers?
3. Do tomatoes do well in pots?
4. What can you grow tomato plants in?
5. Which is larger, determinate varieties or indeterminate varieties?
6. Do determinate varieties grow as large as indeterminate varieties?
7. Do determinate varieties grow as large as indeterminate ones?
8. What size of container is right for tomatoes?
9. Is a 5 gallon container large enough for tomatoes?
10. What is the minimum size of container that tomatoes other than compact determinate varieties require?


Article
----
%s
----

Ten (10) unique questions answered by the article:
"""


# https://ibm.github.io/watsonx-ai-python-sdk/fm_rerank.html
g_rerank_model = Rerank(
   model_id = "cross-encoder/ms-marco-minilm-l-12-v2",
   credentials = g_credentials,
   project_id = g_project_id
)

# https://ibm.github.io/watsonx-ai-python-sdk/fm_embeddings.html
g_embedding_model = Embeddings(
  model_id= "ibm/slate-125m-english-rtrvr",
  credentials = g_credentials,
  project_id = g_project_id
)


def txtGenModel( model_id, prompt_parameters=None ):
    try:
        params = g_prompt_parameters_gen_questions if prompt_parameters is None else prompt_parameters
        model = ModelInference( 
            model_id    = model_id, 
            params      = params, 
            credentials = g_credentials, 
            project_id  = g_project_id 
        )
        return model, ""
    except Exception as e:
        error_str = str( e )
        g_log.writeLog( "my_llm.txtGenModel: " + error_str )
        return None, error_str


def genQuestions( chunk_txt, model=None, prompt_template=None, b_debug=False ):
    prompt_text = g_template_gen_questions % ( chunk_txt ) if prompt_template is None else prompt_template % ( chunk_txt )
    raw_response = g_model_gen_questions.generate( prompt_text ) if model is None else model.generate( prompt_text )
    if b_debug:
        g_log.writeLog( "prompt_text:\n'" + prompt_text + "'\n" )
        g_log.writeLog( "raw_response:\n" + json.dumps( raw_response, indent=3 ) )
    if ( "results" in raw_response ) \
       and ( len( raw_response["results"] ) > 0 ) \
       and ( "generated_text" in raw_response["results"][0] ):
        output = raw_response["results"][0]["generated_text"]
        if re.match( r"(\d\..*)", output ):
            questions_arr = re.findall( r"(\d\..*)", output )
        else:
            questions_arr = re.split( r"[\n\r]+", output )
        #questions_arr = [ re.sub( r"^.*?\d+\.\s*", "", q ) for q in questions_arr ]
        questions_arr_final = []
        for q in questions_arr:
            question_txt = re.sub( r"^.*?\d+\.\s*", "", q )
            if re.match( r"\S", question_txt ):
                questions_arr_final.append( question_txt )
        return output, questions_arr_final
    else:
        return "", []


def rerank( user_question, generated_questions_arr ):
    result = g_rerank_model.generate( query = user_question, inputs = generated_questions_arr ) 
    return result["results"]


def embed( txt_arr ):
    return g_embedding_model.embed_documents( texts = txt_arr )

