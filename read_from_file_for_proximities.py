file_name = '20181119T070913Z (Bennu & Earth collision simulation).csv'
#file_name = 'read_from_file_test.csv'
bodies = [float(fields[1][2:-2]) for fields in [line.split("Closeness:      Bennu and      Earth") for line in open(file_name)] if fields[0] == '']
print(bodies)
print(min(bodies))
