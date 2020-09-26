import os
import glob
from shutil import copy

def CopyContentOfFolder(sauce,destination):
	src_files = os.listdir(sauce)
	for file_name in src_files:
		full_file_name = os.path.join(sauce, file_name)
		if os.path.isfile(full_file_name):
			copy(full_file_name, destination)

def RemoveAllFilesMatching(directory,pattern):
	print(directory+"/*"+pattern)
	FileList = glob.glob(directory+"/*"+pattern)
	for FilePath in FileList:
		try:
			os.remove(FilePath)
		except:
			print("Error in removing misc file")

def get3DModel(protein,ligand):
    try:
        import pymol2
    except ImportError:
        print("🤭 PyMOL 2 has not been installed correctly")
        return None
    session = pymol2.PyMOL()
    session.start()
    cmd = session.cmd
    cmd.load(protein,"target")
    cmd.load(ligand,"ligand")
    cmd.save("model.dae")
    session.stop()