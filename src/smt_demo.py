from z3 import *


RT = [0.32, 0.45, 1.02, 2.0, 1.34]
EC = [0.67, 0.67, 0.45, 0.75, 1.2]
PR = [0.02, 0.45, 0.67, 0.43, 1.0]
RP = [0.75, 0.55, 0.21, 0.68, 0.32]
BL = 1
STOR = [0.5, 0.6, 1, 0.9, 0.65]
CPU = [1, 0.43, 0.86, 0.56, 0.74]
MEM = [0.56, 0.76, 0.54, 0.78, 0.94]
sites = Bools ('MD E1 E2 E3 CD')
rt = 1.0
ec = 0.7
pr = 0.5
rp = 0.5

s = Solver ()
s.add (Or ([sites[i] for i in range (5)]))
s.add ([Implies (sites[i] == True, And (RT[i] <= rt, EC[i] <= ec, PR[i] <= pr)) \
	for i in range (5)])
s.add ([Implies (sites[i] == True, And (RP[i] >= rp, 0 <= RP[i] <= 1)) \
	for i in range (5)])
s.add ([Implies (sites[i] == True, 1 >= BL - EC[i] >= 0) \
	for i in range (5)])
s.add ([Implies (sites[i] == True, And (STOR[i] < 1, CPU[i] < 1, MEM[i] < 1)) \
	for i in range (5)])
print (s)
print (s.check ())

if str (s.check ()) == 'sat':
	print (s.model ()[sites[1]])