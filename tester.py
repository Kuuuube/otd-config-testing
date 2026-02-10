import json
import os
import re

configs_dir = "configs"
config_filenames = os.listdir(configs_dir)
configs = list(map(lambda x: json.loads(open(configs_dir + "/" + x).read()), config_filenames))

tablet_info_dir = "tablet_info"
tablet_infos = []

for config_filename in config_filenames:
    filename_no_ext = config_filename.rsplit(".")[0]
    tablet_info_variant_path = tablet_info_dir + "/" + filename_no_ext
    for test_case in os.listdir(tablet_info_variant_path):
        test_case_path = tablet_info_variant_path + "/" + test_case
        diag_path = test_case_path + "/" + "diag.json"
        strings_path = test_case_path + "/" + "strings.txt"
        
        diag_devices = json.loads(open(diag_path).read())["HID Devices"]
        strings = list(map(lambda x: x.removesuffix("\n").split(": ")[1], open(strings_path).readlines()))

        tablet_infos.append({
            "diag": diag_devices,
            "strings": strings,
            "variant": filename_no_ext,
            "filepath": test_case_path,
        })

for tablet_info in tablet_infos:
    for config in configs:
        for config_identifier in config["DigitizerIdentifiers"]:
            found_identifier_match = False
            for diag_device in diag_devices:
                if config_identifier["VendorID"] == diag_device["VendorID"] and config_identifier["ProductID"] == diag_device["ProductID"] and config_identifier["InputReportLength"] == diag_device["InputReportLength"] and config_identifier["OutputReportLength"] == diag_device["OutputReportLength"]:
                    config_tablet_name = config["Name"].replace("XP-Pen ", "")
                    expected_match = tablet_info["variant"]

                    string_match_success = True
                    for i, string_regex in config_identifier["DeviceStrings"].items():
                        if not re.match(string_regex, tablet_info["strings"][int(i) - 1]):
                            string_match_success = False
                            break

                    if not string_match_success:
                        continue
                    
                    print("Config match hit: " + tablet_info["filepath"])
                    assert(config_tablet_name == expected_match)
                    print("Assert passed")

                    found_identifier_match = True

            if found_identifier_match:
                break
