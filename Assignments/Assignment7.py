import re

# Reading data
data = []
with open("output.csv", "r") as file_:
    for line in file_:
        vals = [list(a) for a in re.findall("R(\d),(\d+\.\d+),(\d+\.\d+),(\d),(\d);", line)]
        data.append(vals)

def get_bucket(wind_intensity):
    return int(wind_intensity*36 - 0.5)

# prepare data
for i in data:
    _ind = 0
    for j in i:
        kostil = i[-1][-1] == '0'
        j.append(_ind)
        _ind+=1
        j.append(len(i))
        j.append(kostil)
        j[0] = int(j[0])
        j[3] = int(j[3])
        j[4] = int(j[4])
        j[1] = get_bucket(float(j[1]))
        j[2] = float(j[2][:6])
#data format: room_type, wind_bucket, smell, gold, action, seq_position, seq_length, leads_to(False - death, True - win) 
rpg = {}
for i in data:
    for j in i:
        key = (j[0], j[1], j[2], j[3])
        if key in rpg:
            rpg[key].append(j)
        else:
            rpg[key] = []
            rpg[key].append(j)
arpg = {}
for key in rpg:
    arpg[key] = [0]*7
    for thing in rpg[key]:
        arpg[key][thing[4]] += ((1) if thing[7] else (-1.0/(thing[6]-thing[5])))
    for i in range(7):
        arpg[key][i] /= len(rpg[key])
    z_exp = [2.718281**i for i in arpg[key]]
    arpg[key] = [i/sum(z_exp) for i in z_exp]
for key in arpg:
    print key, arpg[key]
