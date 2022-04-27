import json
import re

def transform_address(row:dict) -> bool:
    """
    Parses the address into street_address, city, state, zip fields. Invalid address cause a ValueError exception.

    Args:
        row (dict): data row

    Returns:
        bool: True if address is in valid US address format; otherwise False

    Raises:
        ValueError: Unknown address format.
    """
    # regular expression (regex) to match a US address composed of street_address, city, state, zip
    # this regex uses Named Capturing Group feature of regex to assign a name to a matching portion of the string
    # the syntax is (?<group_name>...) where ... contains the matching regex for this group
    address_regex = r"(?P<street_address>[a-zA-Z0-9 .]+)\n(?P<city>[a-zA-Z0-9 ]+), (?P<state>[A-Z]{2}) (?P<zip>[0-9]{5})"
    pattern = re.compile(address_regex)
    # match address using regex
    result = pattern.match(row["registered_address"])
    if result:
        # if a possible match found. assign fields based on regex matching named groups
        row["street_address"] = result.group("street_address")
        row["city"] = result.group("city")
        row["state"] = result.group("state")
        row["zip"] = result.group("zip")
        # delete the original address field
        del row["registered_address"]
        return True
    else:
        address = row["registered_address"].strip().replace("\n", ", ")
        raise ValueError(f"Unknown address format: {address}")

#required fields
VALID_FIELDS = ["license_plate", "make_model", "year", "registered_name", "registered_address", "registered_date"]

def check_schema(row, required_fields=VALID_FIELDS) -> bool:
    '''
    Checks if a json row or dict contains all required fields. Missing fields will cause KeyError exception

    Args:
        row (dict): data row
        fields (set, optional): set of required fields

    Returns:
        bool: True if all fields present

    Raises:
        KeyError: If required fields are missing
    '''
    # Loop through fields to make sure they are all present. If any are missing, raise KeyError.
    for field in required_fields:
        if field not in row:
            raise KeyError(f'Missing required field: {field}')
    return True

def null_check(row:dict, required_fields=VALID_FIELDS) -> bool:
    '''
    Checks the row to ensure no null values. Fields containing null values cause a ValueError

    Args:
        row (dict): data row
        fields (set, optional): set of required fields

    Returns:
        bool: True if none of the fields contain Null values 

    Raises:
        ValueError: If required fields contain none.
    '''
    #Loop through field values to make sure that no values are Null. If they are, return ValueError.
    for field in required_fields:
        if row[field] is None:
            raise ValueError(f"{field} cannot be Null.")
    return True

def run(file_name:str, print_lines:bool=False) -> None:
    """
    From JSON row file read each row

    Args:
        file_name (str): file path to read
        print_lines (bool): print lines from file to console.
    """
    # track the row count
    line_num = 1        # Current line number
    ok_count = 0        # Rows that didn't return an error
    reject_count = 0    # Rows that did return an error
    with open(file_name, "r") as json_file:
        for line in json_file:
            try:
                # read lines into a dict
                row = json.loads(line.strip())
                #transformations
                check_schema(row)
                null_check(row)
                transform_address(row)
                # Print lines
                if print_lines:
                    print(f"[{line_num:04d} [OK]: {row}")
                # line count update
                ok_count += 1
            except Exception as err:
                # print row with error
                print(f"[{line_num:04d}][ERROR:] {str(err)}, [DATA]: {row}")
                reject_count += 1
            finally:
                # Update line count regardless
                line_num += 1
        # Print line count summary
    print(f"Read {line_num - 1} rows")
    print(f"OK rows: {ok_count:04d}, Rejected rows: {reject_count:04d}") 

# Call the function for a test
file_path = "./data/vehicles_complex.json"
run(file_path, print_lines=False)