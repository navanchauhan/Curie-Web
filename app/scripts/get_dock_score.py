#!/usr/bin/python3

import argparse

parser = argparse.ArgumentParser(description="Get Docking Score")
parser.add_argument("-p","--protein",help="Path to protein file")
parser.add_argument("-l","--ligand",help="Path to ligand_out file")

args = parser.parse_args()

if args.protein == None:
    print("Error: Please specify protein file")
    exit(1)
if args.ligand == None:
    print("Error: Please specify ligand file")
    exit(1)


protein = args.protein
ligand = args.ligand

from os.path import basename

print("# " + str(basename(protein)).replace(".pdbqt","") + "-" + str(basename(ligand)).replace("_out.pdbqt",""), end="\n\n")

from tabulate import tabulate

file = open(ligand, "r")
lines = file.readlines()
results = []
i = 1
for line in lines:
    ta = []
    if line.find('REMARK VINA') == 0 and line.split()[3] != "":
        l = line.split()
        ta.append(i)
        ta.append(l[3])
        ta.append(l[4])
        ta.append(l[5])
        i += 1
    if ta != []:
        results.append(ta)

print("## Docking Scores",end="\n\n")
print(tabulate(results,headers=["No.","Affinity","rmsd l.b","rmsd u.b"]))
print("",end="\n\n")
