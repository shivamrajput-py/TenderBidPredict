import json

def load_json(file_path):
    """Load the JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    """Save the JSON file with minified content."""
    with open(file_path, 'w') as file:
        json.dump(data, file, separators=(',', ':'), ensure_ascii=False)

def remove_whitespace(json_string):
    """Minify JSON by removing all unnecessary whitespace."""
    return json.dumps(json.loads(json_string), separators=(',', ':'))

def optimize_json(file_path, output_path):
    """Optimize a JSON file to reduce its size without changing the dataset."""
    print("Loading JSON file...")
    with open(file_path, 'r') as file:
        json_data = file.read()

    print("Minifying JSON file...")
    minified_data = remove_whitespace(json_data)

    print("Saving optimized JSON file...")
    with open(output_path, 'w') as file:
        file.write(minified_data)

    print("Optimization complete. Output saved to:", output_path)

# Example usage
if __name__ == "__main__":
    input_file = "BIDDERS_PROFILE_INSIGHTS_15TO24.json"  # Input JSON file path
    output_file = ("HP_Bidders15to24.json")  # Output JSON file path

    optimize_json(input_file, output_file)
