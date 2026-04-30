'''
utils.py
'''

def _sanitize_binary_name(binary_path) -> str:
    '''Convert binary file path to a safe directory name'''
    return str(binary_path).replace("/", "_")
