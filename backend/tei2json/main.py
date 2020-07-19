#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from multiprocessing.pool import Pool
# import pandas as pd
from pyfiglet import Figlet
from colorama import init, Fore, Style

init()
import os

from teireader import TEIFile
# from ctsreader import CTSFile
# from quotationsreader import QuotationsFile


# Check if virtual environment is running
if os.getenv("VIRTUAL_ENV"):
    pass
# else:
    # print(Fore.RED + "Not using virtual environment" + Style.RESET_ALL)

# Simple CLI for input directory and output filename
def set_up_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "inputdir",
        help="Name of input directory containing TEI XML files. Directory name will also be used for output filenames in /output",
    )
    return parser


# Scan directory for XML files (excluding CTS metadata), return paths
def all_teis(input_dir=""):
    all_xmls = sorted([_ for _ in Path(input_dir).glob("**/*.xml")])
    all_teis = []
    for item in all_xmls:
        if "__cts__.xml" not in item.name:
            all_teis.append(item)
    return all_teis

# Parse XML using TEIFile, return content
def tei_to_csv_entry(tei_file):
    tei = TEIFile(tei_file)
    print(Style.DIM + f"✓ Handled {tei_file}" + Style.RESET_ALL)
    return (
        tei.basename(),
        tei.filepath(),
        tei.title,
        tei.sent,
        tei.received,
        tei.text_plain,
        # tei.text_xml
    )

# Parse TEI XML using TEIFile, return content as dictionary
def tei_to_dictionary(tei_file):
    tei = TEIFile(tei_file)
    print(Style.DIM + f"✓ Handled {tei_file}" + Style.RESET_ALL)
    output = {
        "filename": tei.basename(),
        "title": tei.title,
        "sent": tei.sent,
        "received": tei.received,
        "plain": tei.text_plain,
        # "xml": tei.text_xml
    }
    return output

def main():
    parser = set_up_argparser()
    args = parser.parse_args()
    outputname = str(args.inputdir)

    # Generate list of TEI XML file paths in given input directory
    teis = all_teis(args.inputdir)

    f = Figlet(font="slant")
    print(f.renderText("TEI 2 JSON"))

    # Parse TEI XML into list using multi-threading
    pool = Pool()
    print(Fore.CYAN + "✓ Starting TEI parsing" + Style.RESET_ALL)
    # csv_entries_tei = pool.map(tei_to_csv_entry, teis)
    entries = pool.map(tei_to_dictionary, teis)

    # Create separate JSON files in /output folder
    counter = 0
    for i in entries:
        path = "output/%s.json" % counter
        with open(path, 'w') as json_file:
            try:
                json.dump(i, json_file, indent=4)
                counter += 1
            except:
                print("Error writing JSON file into /output")
                pass

    print(Fore.GREEN + "✓ Completed TEI parsing" + Style.RESET_ALL)

    # Create Pandas dataframe with TEI list data
    # df_tei = pd.DataFrame(
    #     csv_entries_tei,
    #     columns=[
    #         "filename",
    #         "filepath",
    #         "title",
    #         "sender",
    #         "plain",
    #         "xml"
    #     ],
    # )
    # print(Fore.CYAN + "✓ Created Pandas dataframe for TEI data" + Style.RESET_ALL)

    # Generate CSV from list data
    # try:
    #     df_tei.to_csv("output/%s.csv" % outputname, index=False)
    # except:
    #     print(Fore.RED + "Error creating CSV output file" + Style.RESET_ALL)
    # else:
    #     print(
    #         Fore.CYAN + "✓ Generated output CSV file: 'output/%s.csv'" % outputname,
    #         Style.RESET_ALL,
    #     )

    # Generate separate JSON files from list data
    # try:
    #     for i in df_tei.index:
    #         path = ("output/" + df_tei.loc[i]["filename"] + ".json")
    #         df_tei.loc[i].to_json(path)
    # except:
    #     print(Fore.RED + "Error creating single JSON output files" + Style.RESET_ALL)
    # else:
    #     print("✓ Generated single JSON files in 'output/'")

    # Generate single JSON file from list data
    # try:
    #     df_to_json = df_tei.to_json(orient="index")
    #     open("output/%s.json" % outputname, "w").write(df_to_json)
    # except:
    #     print(Fore.RED + "Error creating JSON output file" + Style.RESET_ALL)
    # else:
    #     print(
    #         Fore.CYAN
    #         + "✓ Generated output JSON file: 'output/%s.json'" % outputname
    #         + Style.RESET_ALL
    #     )


if __name__ == "__main__":
    main()