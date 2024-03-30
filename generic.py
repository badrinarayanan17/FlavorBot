import re

# Extracting sessionId

def extractSessionId(session_str:str):
    match = re.search(r"/sessions/(.*?)/contexts/",session_str)
    if match:
        extractedString = match.group(1) # group 1 will be extracting whatever in the bracket
        return extractedString
    
    
def getStringFromFood(food_dict:dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
if __name__ == "__main__":
    print(getStringFromFood({"chole":6,"Ice tea":1}))
    print(extractSessionId("projects/flavorbot-xtxr/agent/sessions/7540caba-6f4b-3e77-f95d-b2890ea2dd49/contexts/ongoing-order"))
    