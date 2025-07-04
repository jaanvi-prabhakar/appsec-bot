from jira_handler import get_transitions

get_transitions("KAN-2")

"""
Transition Name	Transition ID	Resulting Status
In Testing	    "2"	            In Testing
To Do	        "11"	        To Do
In Progress	    "21"	        In Progress
Done	        "31"	        Done
"""