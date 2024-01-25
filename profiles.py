import os
from helpers import load_jsonfile
import applications.broker_agent.tools as tools
import applications.base.tools as base_tools

app_name = "broker_agent"

broker_profile = '''
You are the broker agent of a real estate company;

Your role exclusively involves researching and managing information on real estate properties and companies. Please make this scope of work explicitly clear to the users.

The user will tell you about his lifestyle, you should be able to create a set of search parameters with that information.

Show the recomended parameters for the property search and perform the search to the database inmediately.

If the user's request does not specifically seek information about real estate properties, conclude the interaction with a message and reply TERMINATE 

If the information is located, write a new file using the dump results function and prepare a fulll report of the properties, reply with it then TERMINATE

'''

researcher_profile = '''
You are a world-class researcher, who can do detailed research on any topic and produce facts-based results. You do not make things up, you will try as hard as possible to gather facts & data to back up the research

Please make sure you complete the objective above with the following rules:
1. You should do enough research to gather as much information as possible about the objective.
2. If there are URLs of relevant links and articles, you will scrape them to gather more information
3. After scraping and searching, you should think "Are there any new things I should search and scrape based on the data I collected to increase the research quality?" If the answer is yes, continue; but don't do more than 3 iterations
4. You should not make things up, you should only write facts and data you have gathered
5. In the final output, you should include all reference data & links to back up your research; you should include all reference data and links to back up your research
6. Do not use G2 or LinkedIn, they mostly out outdated data.
'''

# Opening JSON file
cwd = os.getcwd()
app_base_dir = f"{cwd}/applications/{app_name}"
app_fns = load_jsonfile(filename=f"{app_base_dir}/functions.json")
base_fns = load_jsonfile(filename=f"{cwd}/applications/base/functions.json")

def _is_terminate(msg):
    print("IS TERMINATE:", "TERMINATE" in msg["content"])
    return "TERMINATE" in msg["content"]

# Mandatory 
app_proxy_agent_config = {
    "name": "Admin", # Default "ProxyAgent"
    "human_input_mode": "NEVER", # Default NEVER
    "max_consecutive_auto_reply": 5, # default 1
    "system_message": "Interact with the Broker agent to clarify the tasks, reply TERMINATE if the task has been solved", # Optional, but will be better to have some instructions, Default None
    "code_execution_config": {"last_n_messages": 3, "work_dir": f"{app_base_dir}/run_code"}, # Optional, Default None, When the proxy need to run code, sample: {"last_n_messages": 3, "work_dir": "run_code"}   => work_dir must be inside the app and provide the full path
    "is_termination_msg" : _is_terminate, # Mandatory, this sample terminate the execution when the agents messages ends in TERMINATE
    "llm_config": {
            "timeout": 600,
            "temperature": 0,
            "cache_seed": None,
        },
}


def message_filter(msg):
    # Filter, update or change every message input by the user before to be pass to the agents
    return f"{msg} :)"

# Leave empty to work by default
engine_config = {
    "message_filter": message_filter
}

# Available options for llm_config on each agent
# llm_config = {
#     "temperature": 0, # between 0 and 1 determine how creative the agent should be, feel free t play aroudn this value
#     "timeout": 600,
#     "cache_seed": 43,
# }

# Mandatory
# https://platform.openai.com/docs/assistants/tools
agents_config = [
    {
        "name": "Broker Agent",
        "id": "Broker",
        "instructions": broker_profile,
        "function_map": {
            'get_real_estate_info_by_name': tools.get_real_estate_info_by_name, 
            'get_real_estate_listings': tools.get_real_estate_listings, 
            'dump_results_to_file': tools.dump_results_to_file
        },
        "llm_config": {
            "timeout": 600,
            "temperature": 0.5,
            "cache_seed": None,
            "tools": [
                {
                    "type": "function",
                    "function": app_fns["get_real_estate_info_by_name"]
                },
                {
                    "type": "function",
                    "function": app_fns["get_real_estate_listings"]
                },
                {
                    "type": "function",
                    "function": app_fns["dump_results_to_file"]
                }
            ]
        }
    },
    {
        "name": "Researcher",
        "id": "Researcher", # Must fit into this: '^[a-zA-Z0-9_-]{1,64}$'
        "instructions": researcher_profile,
        # "human_input_mode": "NEVER", # Optional, Default NEVER, options [ALWAYS, TERMINATE, NEVER]
        "code_execution_config": None, # Optional, Default None, When the proxy need to run code, sample: {"last_n_messages": 3, "work_dir": "run_code"} => work_dir must be inside the app and provide the full path
        # "is_termination_msg" : None, # Optional, Default None, see above at the app_proxy_agent_config for a sample,
        # "max_consecutive_auto_reply": 1, # default 1
        "function_map": {
            'web_scraping': base_tools.web_scraping, 
            'google_search': base_tools.google_search
        },
        "llm_config": {
            "timeout": 600,
            "temperature": 0,
            "cache_seed": None,
            "tools": [
                {
                    "type": "function",
                    "function": base_fns["google_search"]
                },
                {
                    "type": "function",
                    "function": base_fns["web_scraping"]
                }
            ]
        }
    }
]