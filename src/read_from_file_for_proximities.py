file_name = '2018-11-19 07:09:13.393921 [Bennu & Earth collision simulation].csv'
#file_name = 'read_from_file_test.csv'
bodies = []
for line in open(file_name):
    fields = line.split("Closeness:      Bennu and      Earth")
    if fields[0] == '':
        bodies.append(float(fields[1][2:-2]))
print(bodies)
print(min(bodies))
