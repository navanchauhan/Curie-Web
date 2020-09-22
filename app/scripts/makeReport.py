#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser(description="Make Report Helper Script")
parser.add_argument("-i", "--input", help="Path to report folder")

args = parser.parse_args()

if args.input == None:
    print("Error: Please specify path")
    exit(1)

path = args.input
# path = '/Users/navanchauhan/Desktop/nCOV-19/scripts/pymol/test/'

import untangle
from tabulate import tabulate

# import sys
# report = path + "report.md"
# sys.stdout = open(report, 'w')

from os import listdir
from os.path import isfile, join

onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
image = ""
for x in onlyfiles:
    if ".png" in x and "UNL" in x:
        image = x
import os

fname = os.path.join(path, "report.xml")

doc = untangle.parse(fname)

hi, hb, wb, sb, ps, pc, hab, mc = 0, 0, 0, 0, 0, 0, 0, 0

indexForUNL = 0

for x in doc.report.bindingsite:
    if x.identifiers.longname.cdata == "UNL":
        break
    else:
        indexForUNL += 1


name = doc.report.pdbid.cdata
# print(("# " + (name.replace("_"," ")).replace("PROTEIN","")), end="\n\n")
fallback = 0

print("## Visualisation", end="\n\n")
print(f"![]({image})", end="\n\n")

natural_ligands = []
showNaturalLigands = True

try:
    for x in range(len(doc.report.bindingsite)):
        if doc.report.bindingsite[x]["has_interactions"] == "True" and x != indexForUNL:
            natural_ligands.append(x)
except:
    fallback == 1

if natural_ligands == []:
    showNaturalLigands == False

for ligand in natural_ligands:
    print("### Natural Ligand " + str(ligand+1), end="\n\n")
    if doc.report.bindingsite[ligand].interactions.hydrophobic_interactions.cdata == "":
        print("No Hydrophobic Interactions Found", end="\n\n")
    else:
        print("#### Hydrophobic Interactions", end="\n\n")
        tableBody = []
        tableHeaders = ["No.", "Res.", "AA", "Dist", "Ligand Atom", "Proton Atom"]
        i = 1
        for x in doc.report.bindingsite[
            ligand
        ].interactions.hydrophobic_interactions.hydrophobic_interaction:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.ligcarbonidx.cdata,
                x.protcarbonidx.cdata,
            ]
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")
    if doc.report.bindingsite[ligand].interactions.hydrogen_bonds.cdata == "":
        print("No Hydrogen Bonds Found", end="\n\n")
    else:
        print("## Hydrogen Bonds", end="\n\n")
        tableBody = []
        tableHeaders = [
            "No.",
            "Res.",
            "AA",
            "Dist H-A",
            "Dist D-A",
            "Don Angle",
            "Protisdon?",
            "Sidechain?",
            "D. Atom",
            "A. Atom",
        ]
        i = 1
        for x in doc.report.bindingsite[
            ligand
        ].interactions.hydrogen_bonds.hydrogen_bond:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist_h_a.cdata,
                x.dist_d_a.cdata,
                x.don_angle.cdata,
                x.protisdon.cdata,
                x.sidechain.cdata,
            ]
            l.append((x.donoridx.cdata + "[" + x.donortype.cdata + "]"))
            l.append((x.acceptoridx.cdata + "[" + x.acceptortype.cdata + "]"))
            i += 1
            tableBody.append(l)
            # print(i, x.resnr.cdata, x.restype.cdata, x.dist_h_a.cdata, x.dist_d_a.cdata, x.don_angle.cdata, x.protisdon.cdata, x.sidechain.cdata, (x.donoridx.cdata + "[" + x.donortype.cdata + "]"), (x.acceptoridx.cdata + "[" + x.acceptortype.cdata + "]"))
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

print("## Docked Ligand Interactions", end="\n\n")

try:
    if (
        doc.report.bindingsite[indexForUNL].interactions.hydrophobic_interactions.cdata
        == ""
    ):
        print("No Hydrophobic Interactions Found", end="\n\n")
    else:
        print("**Hydrophobic Interactions Found**", end="\n\n")
        hi = 1
except AttributeError:
    fallback = 1

if fallback == 0:
    if (
        doc.report.bindingsite[indexForUNL].interactions.hydrophobic_interactions.cdata
        == ""
    ):
        print("No Hydrophobic Interactions Found", end="\n\n")
    else:
        print("**Hydrophobic Interactions Found**", end="\n\n")
        hi = 1
    if doc.report.bindingsite[indexForUNL].interactions.hydrogen_bonds.cdata == "":
        print("No Hydrogen Bonds Found", end="\n\n")
    else:
        print("**Hydrogen Bonds Found**", end="\n\n")
        hb = 1
    if doc.report.bindingsite[indexForUNL].interactions.water_bridges.cdata == "":
        print("No Water Bridges Found", end="\n\n")
    else:
        print("**Water Bridges Found**", end="\n\n")
        wb = 1
    if doc.report.bindingsite[indexForUNL].interactions.salt_bridges.cdata == "":
        print("No Salt Bridges Found", end="\n\n")
    else:
        print("**Salt Bridges Found**", end="\n\n")
        sb = 1
    if doc.report.bindingsite[indexForUNL].interactions.pi_stacks.cdata == "":
        print("No Pi Stacks Found", end="\n\n")
    else:
        print("**Pi Stacks Found**", end="\n\n")
        ps = 1
    if (
        doc.report.bindingsite[indexForUNL].interactions.pi_cation_interactions.cdata
        == ""
    ):
        print("No Pi Cation Interactions Found", end="\n\n")
    else:
        print("**Pi Cation Interactions Found**", end="\n\n")
        pc = 1
    if doc.report.bindingsite[indexForUNL].interactions.halogen_bonds.cdata == "":
        print("No Halogen Bonds Found", end="\n\n")
    else:
        print("** Halogen Bonds Found**", end="\n\n")
        hab = 1
    if doc.report.bindingsite[indexForUNL].interactions.metal_complexes.cdata == "":
        print("No Metal Complexes Found", end="\n\n")
    else:
        print("**Metal Complexes Found**", end="\n\n")
        mc = 1

if fallback == 1:
    if doc.report.bindingsite.interactions.hydrophobic_interactions.cdata == "":
        print("No Hydrophobic Interactions Found", end="\n\n")
    else:
        print("**Hydrophobic Interactions Found**", end="\n\n")
        hi = 1
    if doc.report.bindingsite.interactions.hydrogen_bonds.cdata == "":
        print("No Hydrogen Bonds Found", end="\n\n")
    else:
        print("**Hydrogen Bonds Found**", end="\n\n")
        hb = 1
    if doc.report.bindingsite.interactions.water_bridges.cdata == "":
        print("No Water Bridges Found", end="\n\n")
    else:
        print("**Water Bridges Found**", end="\n\n")
        wb = 1
    if doc.report.bindingsite.interactions.salt_bridges.cdata == "":
        print("No Salt Bridges Found", end="\n\n")
    else:
        print("**Salt Bridges Found**", end="\n\n")
        sb = 1
    if doc.report.bindingsite.interactions.pi_stacks.cdata == "":
        print("No Pi Stacks Found", end="\n\n")
    else:
        print("**Pi Stacks Found**", end="\n\n")
        ps = 1
    if doc.report.bindingsite.interactions.pi_cation_interactions.cdata == "":
        print("No Pi Cation Interactions Found", end="\n\n")
    else:
        print("**Pi Cation Interactions Found**", end="\n\n")
        pc = 1
    if doc.report.bindingsite.interactions.halogen_bonds.cdata == "":
        print("No Halogen Bonds Found", end="\n\n")
    else:
        print("** Halogen Bonds Found**", end="\n\n")
        hab = 1
    if doc.report.bindingsite.interactions.metal_complexes.cdata == "":
        print("No Metal Complexes Found", end="\n\n")
    else:
        print("**Metal Complexes Found**", end="\n\n")
        mc = 1

if fallback == 0:
    if hi == 1:
        print("## Hydrophobic Interactions", end="\n\n")
        tableBody = []
        tableHeaders = ["No.", "Res.", "AA", "Dist", "Ligand Atom", "Proton Atom"]
        i = 1
        for x in doc.report.bindingsite[
            indexForUNL
        ].interactions.hydrophobic_interactions.hydrophobic_interaction:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.ligcarbonidx.cdata,
                x.protcarbonidx.cdata,
            ]
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

    if hb == 1:
        print("## Hydrogen Bonds", end="\n\n")
        tableBody = []
        tableHeaders = [
            "No.",
            "Res.",
            "AA",
            "Dist H-A",
            "Dist D-A",
            "Don Angle",
            "Protisdon?",
            "Sidechain?",
            "D. Atom",
            "A. Atom",
        ]
        i = 1
        for x in doc.report.bindingsite[
            indexForUNL
        ].interactions.hydrogen_bonds.hydrogen_bond:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist_h_a.cdata,
                x.dist_d_a.cdata,
                x.don_angle.cdata,
                x.protisdon.cdata,
                x.sidechain.cdata,
            ]
            l.append((x.donoridx.cdata + "[" + x.donortype.cdata + "]"))
            l.append((x.acceptoridx.cdata + "[" + x.acceptortype.cdata + "]"))
            i += 1
            tableBody.append(l)
            # print(i, x.resnr.cdata, x.restype.cdata, x.dist_h_a.cdata, x.dist_d_a.cdata, x.don_angle.cdata, x.protisdon.cdata, x.sidechain.cdata, (x.donoridx.cdata + "[" + x.donortype.cdata + "]"), (x.acceptoridx.cdata + "[" + x.acceptortype.cdata + "]"))
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

    if sb == 1:
        print("## Salt Bridges", end="\n\n")
        tableBody = []
        tableHeaders = [
            "Index",
            "Residue",
            "AA",
            "Distance",
            "Protein positive?",
            "Ligand Group",
            "Ligand Atoms",
        ]
        i = 1
        for x in doc.report.bindingsite[
            indexForUNL
        ].interactions.salt_bridges.salt_bridge:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.protispos.cdata,
                x.lig_group.cdata,
            ]
            atoms = []
            for y in x.lig_idx_list.idx:
                atoms.append(y.cdata)
            l.append(atoms)
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

    if pc == 1:
        print("## Pi Cation Interactions", end="\n\n")
        tableBody = []
        tableHeaders = ["Index", "Residue", "AA", "Distance", "Prot charged?", "Atoms"]
        i = 1
        for x in doc.report.bindingsite[
            indexForUNL
        ].interactions.pi_cation_interactions.pi_cation_interaction:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.offset.cdata,
                x.protcharged.cdata,
            ]
            atoms = []
            for y in x.lig_idx_list.idx:
                atoms.append(y.cdata)
            l.append(atoms)
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")
elif fallback == 1:
    if hi == 1:
        print("## Hydrophobic Interactions", end="\n\n")
        tableBody = []
        tableHeaders = ["No.", "Res.", "AA", "Dist", "Ligand Atom", "Proton Atom"]
        i = 1
        for (
            x
        ) in (
            doc.report.bindingsite.interactions.hydrophobic_interactions.hydrophobic_interaction
        ):
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.ligcarbonidx.cdata,
                x.protcarbonidx.cdata,
            ]
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

    if hb == 1:
        print("## Hydrogen Bonds", end="\n\n")
        tableBody = []
        tableHeaders = [
            "No.",
            "Res.",
            "AA",
            "Dist H-A",
            "Dist D-A",
            "Don Angle",
            "Protisdon?",
            "Sidechain?",
            "D. Atom",
            "A. Atom",
        ]
        i = 1
        for x in doc.report.bindingsite.interactions.hydrogen_bonds.hydrogen_bond:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist_h_a.cdata,
                x.dist_d_a.cdata,
                x.don_angle.cdata,
                x.protisdon.cdata,
                x.sidechain.cdata,
            ]
            l.append((x.donoridx.cdata + "[" + x.donortype.cdata + "]"))
            l.append((x.acceptoridx.cdata + "[" + x.acceptortype.cdata + "]"))
            i += 1
            tableBody.append(l)
            # print(i, x.resnr.cdata, x.restype.cdata, x.dist_h_a.cdata, x.dist_d_a.cdata, x.don_angle.cdata, x.protisdon.cdata, x.sidechain.cdata, (x.donoridx.cdata + "[" + x.donortype.cdata + "]"), (x.acceptoridx.cdata + "[" + x.acceptortype.cdata + "]"))
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

    if sb == 1:
        print("## Salt Bridges", end="\n\n")
        tableBody = []
        tableHeaders = [
            "Index",
            "Residue",
            "AA",
            "Distance",
            "Protein positive?",
            "Ligand Group",
            "Ligand Atoms",
        ]
        i = 1
        for x in doc.report.bindingsite.interactions.salt_bridges.salt_bridge:
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.protispos.cdata,
                x.lig_group.cdata,
            ]
            atoms = []
            for y in x.lig_idx_list.idx:
                atoms.append(y.cdata)
            l.append(atoms)
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")

    if pc == 1:
        print("## Pi Cation Interactions", end="\n\n")
        tableBody = []
        tableHeaders = ["Index", "Residue", "AA", "Distance", "Prot charged?", "Atoms"]
        i = 1
        for (
            x
        ) in (
            doc.report.bindingsite.interactions.pi_cation_interactions.pi_cation_interaction
        ):
            l = [
                i,
                x.resnr.cdata,
                x.restype.cdata,
                x.dist.cdata,
                x.offset.cdata,
                x.protcharged.cdata,
            ]
            atoms = []
            for y in x.lig_idx_list.idx:
                atoms.append(y.cdata)
            l.append(atoms)
            i += 1
            tableBody.append(l)
        print(tabulate(tableBody, headers=tableHeaders), end="\n\n")


