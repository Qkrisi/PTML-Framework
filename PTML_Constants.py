QUOTE = '"'
APOSTROPHE = "'"
IGNORE_ATTRIBUTES = ["id","class"]
DYNAMIC_ROUTE = """
{IndexPath}
@app.route('{Path}')
def Route{Counter}():
    return ReadFromStatic('{Parsed}')
"""
DYNAMIC_ELEMENT = "{Element_Name}=PatchType({Class_Name}, self, {Parent})"