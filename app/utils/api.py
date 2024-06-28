def extract_keys(dictionary, running_id=1):
    """
    Extracts specific keys from a dictionary and adds an "id" key with a running number.

    Args:
        dictionary: The dictionary to extract keys from.
        running_id: The initial value for the "id" key (default: 1).

    Returns:
        A new dictionary containing the extracted keys and the "id" key.
    """
    extracted_data = {
        key: dictionary[key]
        for key in ["hotel_name", "image_url", "description", "unit_cost", "duration"]
        if key in dictionary
    }
    extracted_data["id"] = running_id
    return extracted_data