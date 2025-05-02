#!/usr/bin/env python3

import sys
import re
import subprocess
import numpy as np

def execCmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        sys.exit(1)

def writeXYZ(file_name, num_structures, elements, num_atoms, coordinates):
    with open(file_name, 'w') as f:
        for i in range(num_structures):
            f.write(f"{sum(num_atoms)}\n")
            f.write(f"Frame {i}\n")
            index = 0
            for element, count in zip(elements, num_atoms):
                for _ in range(count):
                    x, y, z = coordinates[index + i * sum(num_atoms)]
                    f.write(f"{element} {x:.6f} {y:.6f} {z:.6f}\n")
                    index += 1

def readFreq(file_name):
    coordinates = []
    dcoordinates = []
    with open(file_name, 'r') as freq_file:
        content = freq_file.readlines()
    index = 2
    while index < len(content):
        line = content[index].strip()
        if line == '':
            break
        line = list(map(float, re.split(r'\s+', line)))
        coordinates.append(np.array([line[0], line[1], line[2]]))
        dcoordinates.append(np.array([line[3], line[4], line[5]]))
        index += 1
    return np.stack(coordinates), np.stack(dcoordinates)

def get_elements_info():
    cmd = "grep 'VRHFIN' OUTCAR"
    content = execCmd(cmd)
    elements = []
    for line in content:
        match = re.search(r'=(.*?):', line)
        if match:
            elements.append(match.group(1))
    cmd = "grep 'ions per type' OUTCAR"
    atom_num = execCmd(cmd)
    num_atoms = list(map(int, re.split(r'\s+', atom_num[0].split('=')[-1].strip())))
    return elements, num_atoms

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} freq1 freq2 ... frames scale")
    sys.exit(1)

print('################ This script makes animation of vibration ################')
elements, num_atoms = get_elements_info()
frames = int(sys.argv[-2])
dframe = 1 / float(frames)
scale = float(sys.argv[-1])

for freq_file in sys.argv[1:-2]:
    print(f'Processing {freq_file}')
    freq_pos, vibration = readFreq(freq_file)
    num_structures = 0
    coordinates = []

    # 0 → +1
    for i in range(frames + 1):
        num_structures += 1
        coordinates.append(freq_pos + vibration * dframe * i * scale)
    # +1 → 0
    for i in range(frames, -1, -1):
        num_structures += 1
        coordinates.append(freq_pos + vibration * dframe * i * scale)
    # 0 → -1
    for i in range(-1, -frames - 1, -1):
        num_structures += 1
        coordinates.append(freq_pos + vibration * dframe * i * scale)
    # -1 → 0
    for i in range(-frames, 0):
        num_structures += 1
        coordinates.append(freq_pos + vibration * dframe * i * scale)

    coordinates = np.concatenate(coordinates)
    writeXYZ(f'{freq_file}.xyz', num_structures, elements, num_atoms, coordinates)

print('------------------ Done ------------------') 