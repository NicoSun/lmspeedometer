"""
Created on Fri Oct 10 22:27:44 2025

@author: nico
"""

import lmstudio as lms
import time
import json


def tokenspeed(model):
    with lms.Client() as client:
        model = lms.llm(model)
        
        start = time.time()
        result = model.respond("Can unicorns summon rainbows? Answer in 150 tokens, +-10%")
        end = time.time()
        tokens = result.stats.predicted_tokens_count
        tokensecond = round(tokens / (end - start),2)
        
        print(result)
        # `result` is the response from the model.
        print("Model used:", result.model_info.display_name)
        print("Predicted tokens:", result.stats.predicted_tokens_count)
        print("Speed:", tokensecond, "t/s")
        print("Stop reason:", result.stats.stop_reason)
        result_dict = {"tokens":result.stats.predicted_tokens_count,"speed":tokensecond,"stop":result.stats.stop_reason}
        return result_dict

def model_loading_test(model):
    try:
        oldmodel = lms.llm()
        oldmodel.unload()
    except:
        #no model loaded
        pass 
    time.sleep(1)

    with lms.Client() as client:
        start = time.time()
        try:
            model = lms.llm(model,ttl=1)
        except:
            #model load error
            return {"duration":"error","size":"error","transfer":"error"}
        end = time.time()
        duration = round(end - start,2)

        model_info = model.get_info()
        model_size = round(model_info.size_bytes / 1e6) # convert to MB
        transfer_rate = round(model_size / duration)
    
    print("Model:", model_info.display_name)
    print("Time:", duration, "seconds")
    print("Size:", model_size, "MB")
    print("Speed:",transfer_rate, "MB/s")
    result_dict = {"duration":duration,"size":model_size,"transfer":transfer_rate}
    return result_dict



#show available models
def load_available_models():
    with lms.Client() as client:
        models = client.llm.list_downloaded()
        models_names = [name.model_key for name in models]
        # print(models_names)
    return models


def load_test_prompts(file_path="testprompts.json"):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Load the JSON data from the file
        data = json.load(file)

    # Accessing and printing each entry
    for entry in data['testprompts']:
        print(f"Type: {entry['type']}")
        print(f"Text: {entry['text']}\n")


# tokenspeed("gemma-3-12b-it")
# load_test_prompts()
# load_available_models()

# model_loading_test("gemma-3-12b-it")
# model_loading_test("openai/gpt-oss-20b")
# model_loading_test("qwen3-32b")
