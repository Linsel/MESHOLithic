import json

def write_dictionary_w_indent_json (file_path,dictionary,indent):  

    # Convert the dictionary to a JSON string
    json_data = json.dumps(dictionary, indent=indent)

    # Save the JSON string to a file
    with open(file_path, 'w') as f:
        f.write(json_data)