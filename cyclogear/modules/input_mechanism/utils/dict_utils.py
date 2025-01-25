from typing import Callable, Dict, List,  Any
import copy

def extract_data(original_dict: Dict[Any, Any], paths_to_extract: List[List[str]]) -> Dict[Any, Any]:
    """
    Extract specific data from a nested dictionary based on provided paths.

    This function traverses a nested dictionary and extracts values specified by
    paths_to_extract, preserving the original structure in the result.

    Parameters:
    - original_dict (Dict[Any, Any]): The original dictionary from which to extract data.
    - paths_to_extract (List[List[str]]): A list of paths, where each path is a list of keys
                                          that specify the nested location of the data to be extracted.

    Returns:
    - Dict[Any, Any]: A new dictionary containing only the extracted data, preserving the
                      hierarchical structure of the original dictionary.
    """
    def recurse(current_dict, current_path, result):
        if isinstance(current_dict, dict):
            for key, value in current_dict.items():
                new_path = current_path + [key]
                if new_path in paths_to_extract:
                    set_nested_value(result, new_path, copy.deepcopy(value))
                recurse(value, new_path, result)

    def set_nested_value(d, path, value):
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    result_dict = {}
    recurse(original_dict, [], result_dict)

    return result_dict

def update_data_subset(data_dict: Dict[Any, Any], subset_dict: Dict[Any, Any], method: Callable, current_path: List[Any]=[]):
    """
    Update the subset dictionary with data from the broader data dictionary using a specified method.

    Args:
        data_dict (Dict[Any, Any]): The dictionary containing updates.
        subset_dict (Dict[Any, Any]): The dictionary to be updated.
        method (Callable): A function that defines how the update should be performed. It should accept
                         three arguments: the subset dictionary, the broader data dictionary, and the current key.
        current_path (List[Any]): A list used internally to track the current path of keys during recursion.
                                This parameter is managed by the function and should not be provided by the caller.
    """
    if isinstance(subset_dict, dict):
        for key in subset_dict:
            new_path = current_path + [key]
            if key in data_dict and isinstance(subset_dict[key], dict) and isinstance(data_dict[key], dict):
                update_data_subset(data_dict[key], subset_dict[key], method, new_path)
            elif key in data_dict:
                method(subset_dict, data_dict, key)

def fetch_data_subset(data_dict: Dict[Any, Any], subset_dict: Dict[Any, Any], method: Callable=None, current_path: List[Any]=[]):
    """
    Update the broader data dictionary with data from the subset dictionary.

    Args:
        data_dict (Dict[Any, Any]): The dictionary to be updated.
        subset_dict (Dict[Any, Any]): The dictionary containing updates.
        method (Callable): A function that defines how the update should be performed. It should accept
                         three arguments: the subset dictionary, the broader data dictionary, and the current key.
        current_path (List[Any]): A list used internally to keep track of the current path of keys
                            during recursion. Users should not provide this parameter; it's managed
                            by the function.
    """
    if isinstance(subset_dict, dict):
        for key in subset_dict:
            new_path = current_path + [key]
            if key in data_dict and isinstance(subset_dict[key], dict) and isinstance(data_dict[key], dict):
                fetch_data_subset(data_dict[key], subset_dict[key], method, new_path)
            elif key in data_dict:
                if method != None:
                    method(data_dict, subset_dict, key)
                else:
                    data_dict[key] = subset_dict[key]

