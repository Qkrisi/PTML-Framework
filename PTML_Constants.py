QUOTE = '"'
APOSTROPHE = "'"
DYNAMIC_ROUTE = """
@app.route('{Path}')
def Route{Counter}():
    return ReadFromStatic('{Parsed}')
"""
DYNAMIC_ELEMENT = "{Element_Name}=PatchType({Class_Name}, self)"