#------------------------------------------------------------------------------#
# Filename: IometerSpecGen.py
# Description:
#   This is a simple script to generate Iometer specifications based on ranges
#  of values. The resulting specification file may then be imported into
#  Iometer. 
#
# Version:
#  .1 - Initially created. - Jeremy Canady


import argparse, os

# Build argument parser.
parser = argparse.ArgumentParser(description='Generates a Iometer specification file based on values provided.')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

parser.add_argument('-fileName', default='iometerSpec.icf')

# Add random settings.
rand_group = parser.add_mutually_exclusive_group(required=True)
rand_group.add_argument('-randomPercentValues', nargs="+", type=int, metavar='<value>')
rand_group.add_argument('-randomPercentIteration', nargs=3, type=int, metavar=('<starValue', '<endValue>', '<iterationSize>'))

# Add transferSize settings.
transfer_group = parser.add_mutually_exclusive_group(required=True)
transfer_group.add_argument('-transferSizeValues', nargs="+", type=int, metavar='<value>')
transfer_group.add_argument('-transferSizeIteration', nargs=2, type=int, metavar=('<starValue>', '<endValue>'))

# Add read percentage.
read_group = parser.add_mutually_exclusive_group(required=True)
read_group.add_argument('-readPercentValues', nargs="+", type=int, metavar='<value>')
read_group.add_argument('-readPercentIteration', nargs=3, type=int, metavar=('<starValue', '<endValue>', '<iterationSize>'))

# Parse the arguments supplied.
opts = vars(parser.parse_args())

# Verify parser input.

# Verify and save the random values.
randomValues = []
if(opts["randomPercentValues"] != None):
	# Verify all the values are within range then save them off.
	for value in opts["randomPercentValues"]:
		if(value < 0 or value > 100):
			print("-randomPercentValues must contains values between 0 and 100")
			exit(0)
		randomValues = opts["randomPercentValues"]
else:
	# Verify the iteration range values are valid then build the range.
	if(opts["randomPercentIteration"][0] < opts["randomPercentIteration"][1] # Verify the start value is smaller than the end.
		and opts["randomPercentIteration"][0] >= 0 and opts["randomPercentIteration"][0] <= 100 # Verify the start value is within range.
		and opts["randomPercentIteration"][1] >= 0 and opts["randomPercentIteration"][1] <= 100 # Verify the end value is in range.
		and opts["randomPercentIteration"][2] > 0): # Verify the iterator value is not negative.

		tempValue = opts["randomPercentIteration"][0]
		while tempValue <= opts["randomPercentIteration"][1]:
			randomValues.append(tempValue)
			tempValue += opts["randomPercentIteration"][2]
	else:
		print('-randomPercentIteration must have valid start, end and iteration values')
		exit(0)

# Verify and save read values
readValues = []
if(opts["readPercentValues"] != None):
	# Verify all the values are within range then save them off.
	for value in opts["readPercentValues"]:
		if(value < 0 or value > 100):
			print("-readPercentValues must contains values between 0 and 100")
			exit(0)
		readValues = opts["readPercentValues"]
else:
	# Verify the iteration range values are valid then build the range.
	if(opts["readPercentIteration"][0] < opts["readPercentIteration"][1] # Verify the start value is smaller than the end.
		and opts["readPercentIteration"][0] >= 0 and opts["readPercentIteration"][0] <= 100 # Verify the start value is within range.
		and opts["readPercentIteration"][1] >= 0 and opts["readPercentIteration"][1] <= 100 # Verify the end value is in range.
		and opts["readPercentIteration"][2] > 0): # Verify the iterator value is not negative.

		tempValue = opts["readPercentIteration"][0]
		while tempValue <= opts["readPercentIteration"][1]:
			readValues.append(tempValue)
			tempValue += opts["readPercentIteration"][2]
	else:
		print('-readPercentIteration must have valid start, end and iteration values')
		exit(0)

# Verify and save rthe transfer size
transferSizeValues = []
if(opts["transferSizeValues"] != None):
	# Verify all the values are within range then save them off.
	for value in opts["transferSizeValues"]:
		if(value < 0 or value > 131072):
			print("-transferSizeValues must contains values between 0 and 100")
			exit(0)
		transferSizeValues = opts["transferSizeValues"]
else:
	# Verify the iteration range values are valid then build the range.
	if(opts["transferSizeIteration"][0] < opts["transferSizeIteration"][1] # Verify the start value is smaller than the end.
		and opts["transferSizeIteration"][0] > 0 and opts["transferSizeIteration"][0] <= 131072 # Verify the start value is within range.
		and opts["transferSizeIteration"][1] > 0 and opts["transferSizeIteration"][1] <= 131072): # Verify the end value is in range.

		tempValue = opts["transferSizeIteration"][0]
		while tempValue <= opts["transferSizeIteration"][1]:
			transferSizeValues.append(tempValue)
			tempValue += tempValue
	else:
		print('-transferSizeIteration must have valid start, end and iteration values')
		exit(0)

# Write the spec file.
outFile = open(opts["fileName"], "w")
outFile.write("Version 2008.10.23")
outFile.close()
outFile = open(opts["fileName"], "a")
outFile.write("\n'ACCESS SPECIFICATIONS =========================================================")

# Generate the spec file.
for trans in transferSizeValues:
	for rand in randomValues:
		for readP in readValues:
			outFile.write("\n'Access specification name,default assignment")
			tempName = "\n\tTrans:%i; Rand:%i; Read:%i,default assignment" % (trans, rand, readP)
			outFile.write(tempName)
			outFile.write("\n'size,% of size,% reads,% random,delay,burst,align,reply")
			tempValues = "\n\t%iK,100,%i,%i,0,1,0,0" % (trans*1024, readP, rand)
			outFile.write(tempValues)

# Finish file.
outFile.write("\n'END access specifications")
outFile.write("\nVersion 2008.10.23 ")
outFile.close()
print("\n")
print("Total Specifications Generated: " + str(len(transferSizeValues) * len(randomValues) * len(readValues)))
print("File Saved To: " + os.path.abspath(outFile.name))