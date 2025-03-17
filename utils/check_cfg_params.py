import configparser
import argparse

def read_cfg_to_dict(file_path):
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case sensitivity
    try:
        with open(file_path) as f:
            config.read_file(f)
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {e}")

    return {section: dict(config.items(section)) for section in config.sections()}

def validate_config(actual_cfg, expected_cfg, file_path):
    mismatches = []
    flag = 0

    #  Compare expected vs actual values
    for section, expected_params in expected_cfg.items():
        if section in actual_cfg:
            for key, expected_value in expected_params.items():
                actual_value = actual_cfg[section].get(key)

                # Case 1: SHOULD_NOT_BE_PRESENT — key should not exist
                if expected_value == "SHOULD_NOT_BE_PRESENT":
                    if actual_value is not None:
                        mismatches.append(
                            f"Error: '{key}' should not be present in section [{section}] in {file_path}"
                        )
                        flag = 1

                # Case 2: Expected value is present but wrong
                else:
                    if actual_value is None:
                        mismatches.append(
                            f"Error: '{key}' is missing in section [{section}] in {file_path}"
                        )
                        flag = 1
                    elif actual_value != expected_value:
                        mismatches.append(
                            f"'{key}' in section [{section}] is '{actual_value}', expected '{expected_value}'"
                        )
                        flag = 1
        else:
            # Case 3: Missing section entirely (if keys are not marked as SHOULD_NOT_BE_PRESENT)
            if not all(value == "SHOULD_NOT_BE_PRESENT" for value in expected_params.values()):
                mismatches.append(
                    f"Error: Section [{section}] is missing in {file_path}"
                )
                flag = 1

    return mismatches, flag

def main():
    parser = argparse.ArgumentParser(description="Compare multiple .cfg files with a single expected .cfg file")
    parser.add_argument('--input_files', type=str, required=True,
                        help="Comma-separated list of input .cfg files to validate")
    parser.add_argument('--default_file', type=str, required=True,
                        help="Path to the expected .cfg file")

    args = parser.parse_args()

    input_files = args.input_files.split(",")
    expected_file = args.default_file

    # Read expected config
    expected_config = read_cfg_to_dict(expected_file)

    overall_flag = 0
    for file in input_files:
        actual_config = read_cfg_to_dict(file)

        mismatch_list, flag = validate_config(actual_config, expected_config, file)

        if mismatch_list:
            print(f"\n Mismatches in '{file}':")
            print("\n".join(mismatch_list))
        else:
            print(f" All parameters in '{file}' match the expected configuration.")

        overall_flag = max(overall_flag, flag)

    print("\n Overall Execution flag:", overall_flag)
    return overall_flag

if __name__ == "__main__":
    exit(main())
