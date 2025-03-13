import configparser
import argparse
import os


def read_cfg_to_dict(file_path):
    """Reads a .cfg file and converts it to a dictionary."""
    config = configparser.ConfigParser()
    config.read(file_path)
    return {section: dict(config.items(section))
            for section in config.sections()}


def validate_config(actual_cfg, expected_cfg, file1_cfg_path):
    """Compares actual (A.cfg) and expected (B.cfg) configurations and prints mismatches."""
    mismatches = []
    flag = 0  # Default flag is 0 (graceful execution)

    # Check for ANY field marked as 'SHOULD_NOT_BE_PRESENT' in expected config
    for section, expected_params in expected_cfg.items():
        for key, expected_value in expected_params.items():
            if expected_value == "SHOULD_NOT_BE_PRESENT":
                if section in actual_cfg and key in actual_cfg[section]:
                    mismatches.append(
                        f"Error: '{key}' should not be present in section [{section}] in {file1_cfg_path}")
                    flag = 1

    # Standard comparison for other parameters
    for section, expected_params in expected_cfg.items():
        if section in actual_cfg:
            for key, expected_value in expected_params.items():
                if expected_value == "SHOULD_NOT_BE_PRESENT":
                    continue  # Skip as this is handled above

                actual_value = actual_cfg[section].get(key)
                if actual_value is None:
                    mismatches.append(
                        f"{key} is missing in section [{section}] {file1_cfg_path}")
                    flag = 1  # Set flag on missing key
                elif actual_value != expected_value:
                    mismatches.append(
                        f"{key} in section [{section}] is {actual_value}, expected {expected_value}")
                    flag = 1  # Set flag on value mismatch
        else:
            # skip if the entire section has ONLY `SHOULD_NOT_BE_PRESENT`
            # fields
            if all(
                    value == "SHOULD_NOT_BE_PRESENT" for value in expected_params.values()):
                continue
            mismatches.append(
                f"Section [{section}] is missing in {file1_cfg_path}")
            flag = 1  # Set flag on missing section

    return mismatches, flag


# Use argparse to take file paths as arguments
os.chdir('..')
os.chdir('cfgfiles')
parser = argparse.ArgumentParser(
    description="Compare multiple .cfg files with a single expected .cfg file")
parser.add_argument('actual_files', nargs='+', type=str,
                    help="Path to the actual .cfg files")
parser.add_argument(
    'expected_file',
    type=str,
    help="Path to the expected .cfg file")

# Parse the arguments
args = parser.parse_args()

# Read expected config
expected_config = read_cfg_to_dict(args.expected_file)

# Compare each actual config file against the expected config
overall_flag = 0
for file in args.actual_files:
    print(f"\nComparing '{file}' with '{args.expected_file}'")
    actual_config = read_cfg_to_dict(file)
    mismatch_list, flag = validate_config(actual_config, expected_config, file)

    if mismatch_list:
        print("\n".join(mismatch_list))
    else:
        print(f"All parameters in '{file}' match the expected configuration.")

    # Set overall flag if any comparison fails
    overall_flag = max(overall_flag, flag)

# Final execution flag summary
print("\nOverall Execution flag:", overall_flag)

print("Triggering GitHub Action...")
