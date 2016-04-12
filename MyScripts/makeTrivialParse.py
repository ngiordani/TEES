import sys

with open(sys.argv[1]) as f:
    lines = f.readlines()
out = open(sys.argv[1], 'wb')

for line in lines:
    if not line.strip():
        out.write('\n')
        continue
    fields = line.strip().split('\t')
    #fields[6] = str(int(fields[0])-1)
    if fields[6] == '0': fields[7] = "root"
    else: fields[7] = "dep"
    out.write('\t'.join(fields)+'\n')

out.close()
