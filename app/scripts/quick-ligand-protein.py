#!/usr/bin/python3
import argparse

# import logzero
# import logging
# from logzero import logger as log
import pymol2
import time

import os

print(os.getcwd())

#################
# Configuration #
#################

startTime = time.time()
version = "1.0"
desc_text = "PyMol Quick Visualtion " + version
ligandColor = "red"
# logzero.loglevel(logging.INFO)
height = 1000
width = 800
dpi = 300
ray = 0


m1 = "target"
m2 = "ligand"

parser = argparse.ArgumentParser(description=desc_text)
parser.add_argument("-p", "--protein", help="Path to protein file")
parser.add_argument("-l", "--ligand", help="Path to ligand_out file")
parser.add_argument("-c", "--color", help="Color for ligand in visualisation")

args = parser.parse_args()

if args.protein == None:
    print("Error: Please specify protein file")
    exit(1)
if args.ligand == None:
    print("Error: Please specify ligand file")
    exit(1)
if args.color == None:
    print("No color was speciifed, using default settings.")

protein = args.protein
print("Protein: ", protein)
ligand = args.ligand


def loadMol(filename, name):
    print("Loading " + filename + " as " + name)
    cmd.load(filename, name)


def changeColor(name, colorName):
    print("Changed " + name + "'s color to " + colorName)
    cmd.color(colorName, name)


def orientEtZoom():
    cmd.orient()
    cmd.zoom()


def showSurface(name):
    cmd.show("surface", name)


def surfaceTransparency(amount):
    print("Changed surface transparency to " + str(amount * 100) + "%")
    cmd.set("transparency", amount)


def generatePNG(filename, height=height, width=width, dpi=dpi, ray=ray):
    print("Generating " + filename + ".png")
    cmd.png(filename, height, width, dpi=dpi, ray=ray)


def flipHorizontal():
    cmd.rotate("y", 180)


def zoomTo(name):
    cmd.zoom(name)


def generatePictures():
    generatePNG("output-front")
    flipHorizontal()
    generatePNG("output-back")
    zoomTo(m2)
    generatePNG("closeup-back")
    orientEtZoom()
    flipHorizontal()
    zoomTo(m2)
    generatePNG("closeup-front")


print("Initialising PyMol")
session = pymol2.PyMOL()
print("Starting PyMol Session")
session.start()
cmd = session.cmd

loadMol(protein, m1)
cmd.remove("resn hoh")  # remove water
loadMol(ligand, m2)
changeColor(m1, "grey60")
changeColor(m2, ligandColor)
cmd.color("blue", "hetatm")  # color heteroatoms
orientEtZoom()
showSurface(m1)
surfaceTransparency(0.6)

generatePictures()

endTime = time.time()
print("Finished Execution in " + str(round((endTime - startTime), 2)) + " seconds.")
