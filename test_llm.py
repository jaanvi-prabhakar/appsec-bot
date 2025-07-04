from urllib import response
from llm_handler import generate_remediation_response

if __name__ == "__main__":
    response = generate_remediation_response("SQLi", "Found SQL Injection in login endpoint.")
    print("\nRemediation suggestion: \n")
    print(response)