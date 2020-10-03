#!/bin/bash
echo "$(pwd)"
currentVersion="0.9"
protein="false"
ligand="false"
docking="false"
visualisations="false"
interactions="false"
proteinPath=""
ligandPath=""
pdfPath=""
smile=""
name="report"
config=""

usage()
{
  cat <<EOF
Curie-CLI
Description: OwO.
Usage: curie [flags] or curie [-a] [arg] [-s] [arg]
  -d  Perform Docking using AutoDock Vina
  -p  Visualisations using PyMOL
  -i  Protein-Ligand Interactions using PLIP
  -s  SMILES Code for Ligand
  -n  Name for ligand if using the -s option
  -r  Specify Receptor file path (PDBQT Format Only!)
  -l  Specify Ligand file path (PDBQT Format Only!)
  -c  Specify AutoDock Vina Configuration File (TXT Format Only!)
  -h  Show the help
  -v  Get the tool version
Examples:
   ./main.sh -v
   ./main.sh -v
EOF
}


while getopts "r:l:s:n:c:vhdip" opt; do
  case "$opt" in
    \?) echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    h)  usage
        exit 0
        ;;
    v)  echo "Version $currentVersion"
        exit 0
        ;;
    u)
        getConfiguredClient || exit 1
        checkInternet || exit 1
        update
        exit 0
        ;;
    d) 
        docking="true"
        ;;
    i)
        interactions="true"
        ;;
    p)
        visualisations="true"
        ;;
    s)
       smile="$OPTARG"
        ;;
    n) 
       name="$OPTARG"
       ;;
    r)
       proteinPath="$OPTARG"
        ;;
    l)
       ligandPath="$OPTARG"
        ;;
    c) 
        config="$OPTARG"
        ;;
    a)
        artist="true"
        if [[ "$(echo "$@" | grep -Eo "\-s")" == "-s" ]];then song="true";fi # wont go through both options if arg spaced and not quoted this solves that issue (dont need this but once had bug on system where it was necessary)
        if [[ "$(echo "$@" | grep -Eo "\-f")" == "-f" ]];then filePath=$(echo "$@" | grep -Eo "\-f [ a-z A-Z / 0-9 . \ ]*[ -]?" | sed s/-f//g | sed s/-//g | sed s/^" "//g);fi
      ;;
    #s)
    #    song="true"
    #    if [[ "$(echo "$@" | grep -Eo "\-a")" == "-a" ]];then artist="true";fi # wont go through both options if arg spaced and not quoted this solves that issue (dont need this but once had bug on system where it was necessary)
    #    if [[ "$(echo "$@" | grep -Eo "\-f")" == "-f" ]];then filePath=$(echo "$@" | grep -Eo "\-f [ a-z A-Z / 0-9 . \ ]*[ -]?" | sed s/-f//g | sed s/-//g | sed s/^" "//g);fi
    #  ;;
    :)  echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
  esac
done

if [[ $# == "0" ]]; then
  usage ## if calling the tool with no flags and args chances are you want to return usage
  exit 0
elif [[ $# == "1" ]]; then
  if [[ $1 == "update" ]]; then
    getConfiguredClient || exit 1
    checkInternet || exit 1
    update || exit 1
    exit 0
  elif [[ $1 == "help" ]]; then
    usage
    exit 0
  fi
fi

if [[ $docking == "true" ]]; then
    if [[ $proteinPath != "" ]]; then
        if [[ $smile != "" ]] || [[ $ligandPath != "" ]]; then
            if [[ $config == "" ]]; then
                echo "Configuration File Not Specified!"
                exit 1
            else
                dockingCheck="true"
            fi
        else 
            echo "WTF Only Protein!"
            exit 1
        fi
    fi
fi

if [[ $smile != "" ]]; then
    if [[ $name == "" ]]; then
        name="ligand"
        obabel -:"$smile" --gen3d -opdbqt -O$name.pdbqt
        ligandPath="$name.pdbqt"
    fi
fi

if [[ $dockingCheck == "true" ]]; then
    echo ""
    vina --receptor $proteinPath --ligand $ligandPath --config $config
fi



if [[ $interactions == "true" ]]; then
    file=$(echo "$ligandPath" | cut -f 1 -d '.')
    python3 ./get-best.py -p $proteinPath -l "$(echo $file)_out.pdbqt"
    echo "Generating SVG of Compound"
    obabel $ligandPath -O compound.svg
    echo "Running PLIP"
    plip -f best.pdb -qpxy
    echo "Getting Dock Score"
    python3 ./get_dock_score.py -l "$(echo $file)_out.pdbqt" -p $proteinPath > report.md
    echo "Making partial report"
    python3 ./makeReport.py --input . >> report.md
    if [[ $visualisations == "true" ]]; then
        echo "Creating Visualisations"
        python3 ./quick-ligand-protein.py -p $proteinPath -l "$(echo $file)_out.pdbqt"
        python3 ./add-pictures.py >> report.md
    fi
    echo "Generating PDF"
    pandoc -V geometry:margin=1in report.md --pdf-engine=xelatex -o $name.pdf
fi

#echo "$proteinPath and $ligandPath and $docking and $interactions and $visualisations"
