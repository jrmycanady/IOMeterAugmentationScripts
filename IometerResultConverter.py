#------------------------------------------------------------------------------#
# Filename: IometerResultConverter.py
# Description:
#   This script converts the Iometer result file into a simple CSV format for
#  importing into a speadsheet software. It can also convert to a sqlite
#  database.
#
# Version:
#  .1 - Initially created. - Jeremy Canady
#  .2 - Corrected a CSV formatting issue. - Jeremy Canady

import argparse, os, re

# Build argument parser.
parser = argparse.ArgumentParser(description='Converts an Iometer result file to either a CSV file or SQLite database.')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

parser.add_argument('resultFile')
parser.add_argument('-outputFile', default='result.csv')
parser.add_argument('-SQLite', action='store_true')

opts = vars(parser.parse_args())

# Check to see if they wanted SQLite. If so verify they have the SQLite library.
# Also fail if the db already exists.
if(opts["SQLite"]):
	try:
		import sqlite3
	except ImportError:
		print('The SQLite 3 library is missing.')
		exit(0)

	if(os.path.isfile(opts["outputFile"])):
		print('Output database file already exists.')
		exit(0)

# Prepare the regular expressions.
pat_spec_name = re.compile("\'Access specification name")
pat_spec_config = re.compile("(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)")
pat_spec_result = re.compile('^ALL,All,.*?,\d,\d,\d,(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+)')
pat_spec_name_select = re.compile("(.*?),")


# Attempt to open the file for reading.
try:
	result_file = open(opts["resultFile"], 'r')

	# Prepare the output or database.
	if(opts["SQLite"]):
		con = sqlite3.connect(opts["outputFile"])
		cur = con.cursor()
		cur.execute('create table iostats ( name varchar(100), transfer_size integer, read_percent integer, random_percent integer, total_iops real, total_read_iops real, total_write_iops real, total_mbps real, total_read_mbps real, total_write_mbps real, total_avg_response_time real, total_avg_read_response_time real, total_avg_write_response_time real);')

	else:
		output_file = open(opts["outputFile"], 'w')
		output_file.write('"spec_name","transfer_size","read_percent","random_percent","total_iops","total_read_iops","total_write_iops","total_mbps","total_read_mbps","total_write_mbps","total_avg_response_time","total_avg_read_response_time","total_avg_write_response_time"')
		output_file.close()
		output_file = open(opts["outputFile"], 'a')

	# Parse and build the new file.
	line = result_file.readline()
	while line:
		# Look for a line with the specification name.
		temp = pat_spec_name.match(line)
		if temp:

			# Save the spec name.
			match = pat_spec_name_select.match(result_file.readline())
			spec_name = match.group(1)
			#spec_name = result_file.readline()
			
			# Read off the config header line.
			result_file.readline()
			
			# Read the config.
			line = result_file.readline()
			
			# Parse and save the config line.
			match = pat_spec_config.match(line)
			spec_trans = match.group(1)
			spec_read = match.group(3)
			spec_rand = match.group(4)

			# Read off useless lines
			result_file.readline()
			result_file.readline()
			result_file.readline()

			# Read off IO results
			line = result_file.readline()

			match = pat_spec_result.match(line)
			total_iops = match.group(1)
			total_read_iops = match.group(2)
			total_write_iops = match.group(3)
			total_mbps = match.group(4)
			total_read_mbps = match.group(5)
			total_write_mbps = match.group(6)
			total_avg_response_time = match.group(12)
			total_avg_read_response_time = match.group(13)
			total_avg_write_response_time = match.group(14)

			if(opts["SQLite"]):
				query = "INSERT INTO iostats(name,  transfer_size, read_percent, random_percent, total_iops, total_read_iops, total_write_iops, total_mbps, total_read_mbps, total_write_mbps, total_avg_response_time, total_avg_read_response_time, total_avg_write_response_time ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"""
				cur.execute(query, (spec_name, spec_trans, spec_read, spec_rand, total_iops, total_read_iops, total_write_iops, total_mbps, total_read_mbps, total_write_mbps, total_avg_response_time, total_avg_read_response_time, total_avg_write_response_time,))
				con.commit()
			else:
				output_file.write("\n" + '"' + spec_name + '","' + spec_trans + '","' + spec_read + '","' + spec_rand + '","' + total_iops + '","' + total_read_iops + '","' + total_write_iops + '","' + total_mbps + '","' + total_read_mbps + '","' + total_write_mbps + '","' + total_avg_response_time + '","' + total_avg_read_response_time + '","' + total_avg_write_response_time + '"')

		line = result_file.readline()

except IOError:
	print('Failed to open files')
	exit(0)
else:
	result_file.close()
	
	if(opts["SQLite"]):
		cur.close()
	else:
		output_file.close()
	