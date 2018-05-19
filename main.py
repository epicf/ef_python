import re
import sys
import argparse
import configparser

import h5py

from Domain import Domain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_or_h5_file", help="Config or h5 file")
    args = parser.parse_args()
    config_or_h5_file = args.config_or_h5_file
    continue_from_h5 = False
    dom, continue_from_h5 = construct_domain(config_or_h5_file)
    if continue_from_h5:
        dom.continue_pic_simulation()
    else:
        dom.start_pic_simulation()
    return 0


def construct_domain(config_or_h5_file):
    extension =	config_or_h5_file[config_or_h5_file.rfind(".") + 1:]
    if extension == "h5":
        with h5py.File(config_or_h5_file, 'r') as h5file:
            filename_prefix, filename_suffix = \
                extract_filename_prefix_and_suffix_from_h5filename(config_or_h5_file)
            dom = Domain.init_from_h5(h5file, filename_prefix, filename_suffix)
            continue_from_h5 = True
    else:
        conf = configparser.ConfigParser()
        conf.read(config_or_h5_file)
        echo_config(config_or_h5_file, conf)
        dom = Domain.init_from_config(conf)
        continue_from_h5 = False
    return dom, continue_from_h5


def echo_config(config_or_h5_file, conf):
    print("Config file is: ", config_or_h5_file)
    for s in conf.sections():
        print("[", s, "]")
        for k, v in conf[s].items():
            print("{} = {}".format(k, v))


def extract_filename_prefix_and_suffix_from_h5filename(h5_file):
    rgx = "[0-9]{7}" # search for timestep in filename (7 digits in a row)
    match = re.search(rgx, h5_file)
    if match:
        prefix = h5_file[0:match.start()]
        suffix = h5_file[match.end():]
        print("Extracted h5 prefix and suffix:", prefix, suffix)
    else:
        print("Can't identify filename prefix and suffix in ", h5_file)
        print("Aborting.")
        sys.exit(-1)
    return prefix, suffix


if __name__ == "__main__":
    main()
