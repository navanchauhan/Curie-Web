#!/usr/bin/python3
import argparse
import pymol2
import re

#################
# Configuration #
#################

version = "1.0"
desc_text = "PyMol Quick Visualtion " + version

parser = argparse.ArgumentParser(description=desc_text)
parser.add_argument("-p","--protein",help="Path to protein file")
parser.add_argument("-l","--ligand",help="Path to ligand_out file")

args = parser.parse_args()

def li(s):
    #log.info(s)
    None


if args.protein == None:
    print("Error: Please specify protein file")
    exit(1)
if args.ligand == None:
    print("Error: Please specify ligand file")
    exit(1)

print("Getting Best ligand from",args.protein,args.ligand)

protein = args.protein
ligand = args.ligand

session = pymol2.PyMOL()
session.start()
cmd = session.cmd
cmd.load(protein,'pro')
cmd.load(ligand,'lig')
cmd.split_states('lig')

#fname = re.sub(r'^.*?/', '', protein.replace(".pdbqt","")) + "-" + re.sub(r'^.*?/', '', ligand.replace(".pdbqt","")) + ".pdb" 

cmd.save("best.pdb","pro lig_0001")
