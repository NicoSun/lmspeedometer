"""
Created on Fri Oct 10 22:27:44 2025

@author: nico
"""

import lmstudio as lms
import time
import json

class LmBenchmarks:
    """ The benchmark class connects to LM Studio and 
    """
    def __init__(self):
        self.check_lmstudio()

    def check_lmstudio(self):
        '''Checks the LM Studio connection '''
        with lms.Client() as client:
            models = client.llm.list_downloaded()

    def tokenspeed(self,model,length):
        '''Benches the LLM execution speed in token per second
             Args: llm_model, benchmark_length (short, medium, long)

            Returns: a list of becnhmark results (tokens, speed, stopReason)       
         '''
        with lms.Client() as client:
            model = lms.llm(model)

            prompt = testprompts.return_prompt(length)

            start = time.perf_counter()
            result = model.respond(prompt)
            end = time.perf_counter()
            tokens = result.stats.predicted_tokens_count
            tokensecond = round(tokens / (end - start),2)
            
            # print(result)
            # `result` is the response from the model.
            print("Model used:", result.model_info.display_name)
            print("Predicted tokens:", result.stats.predicted_tokens_count)
            print("Speed:", tokensecond, "t/s")
            print("Stop reason:", result.stats.stop_reason)
            result_dict = {"tokens":result.stats.predicted_tokens_count,"speed":tokensecond,"stop":result.stats.stop_reason, "result":result}
            return result_dict

    def model_loading_test(self,model):
        '''Benches the LLM loading speed in megabyte per second (MB/s)
             Args: llm_model

            Returns: a list of becnhmark results (duration (s), size (MB), transfer_rate (MB/s)       
         '''

        try:
            oldmodel = lms.llm()
            oldmodel.unload()
        except:
            #no model loaded
            pass 
        time.sleep(1)

        with lms.Client() as client:
            start = time.perf_counter()
            try:
                model = lms.llm(model,ttl=1)
            except Exception as e:
                print(e)
                #model load error
                return {"duration":"error","size":"error","transfer":e}
            end = time.perf_counter()
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
    def load_available_models(self):
        """ Loads all avaliable models for the GUI user selection """
        with lms.Client() as client:
            models = client.llm.list_downloaded()
            models_names = [name.model_key for name in models]
            # print(models_names)
        return models


class Testprompts:
    """ A class to load the prompts for benchmarking from benchprompts.json"
         or create it with default prompts if none exists.
    """
    def __init__(self):
        self.check_prompt_file()
        self.prompts = {}
        self.load_bench_prompts()

    def load_bench_prompts(self,file_path="benchprompts.json"):
        """ Loads the benchmark prompts """

        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Load the JSON data from the file
            data = json.load(file)

        for k,v in data.items():
            self.prompts[k] = v
        
    def return_prompt(self, length):
        """ returns the benchmark prompts """
        return self.prompts[length]

    def print_testprompts(self):
        """ print the benchmark to terminal """
        # Accessing and printing each entry
        print(self.prompts)

    def check_prompt_file(self, file_path="benchprompts.json"):
        """ loads bench prompts from benchprompts.json or creates a new file if it doesn't exist """
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {
            "short": 'Count from 1 to 12',
            "medium": 'Write a Python Script which assigns a mood to a unicorn for each month of the year.',
            "long": 'code a snake game in C++'
            }

            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            print(e)

testprompts = Testprompts()