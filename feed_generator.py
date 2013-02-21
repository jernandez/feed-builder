#! /usr/bin/env python
import time, sys, csv, xml, re, subprocess
import logging
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from optparse import OptionParser

###################################################################
# Nuts and bolts
###################################################################
# Global error log
errors = ''
# Global dictionaries
brand_dict = {}
category_dict = {}

def populateTags(parentTag, tagTitle, tagText):
	if not isinstance(tagText, str):
		node = SubElement(parentTag, tagTitle+'s')
		for item in tagText:
			subNode = SubElement(node, tagTitle)
			subNode.text = item
	else:
		node = SubElement(parentTag, tagTitle)
		node.text = tagText

def returnNode(line, value, options, xmlIndex=0):
	global errors
	try:
		if options.feedtype == 'csv':
			return line[value]
		elif options.feedtype == 'xml':
			return str(line.getElementsByTagName(value)[xmlIndex].firstChild.nodeValue)
	except:
		errors += '\nMissing: ' + str(value) + ': Line ' + str(line)
		return 0

def returnNodeList(line, value, options):
	global errors
	try:
		if options.feedtype == 'csv':
			return [item for item in returnNode(line,value,options).split('|')]
		elif options.feedtype == 'xml':
			return [returnNode(line,value,options,idx) for idx,item in enumerate(line.getElementsByTagName(value))]
	except:
		return 0

def checkNode(line, key, value, options, product_map):
	global errors
	global brand_dict
	global category_dict
	if key == 'BrandExternalId':
		try:
			brand_id = returnNode(line,product_map['BrandExternalId'],options)
			brand_dict[brand_id] = {
				'ExternalId': brand_id,
				'Name': returnNode(line,product_map['Brand'],options)
			}
			return brand_id
		except:
			errors += 'exception: ' + str(key) + str(line)
			return 0
	elif key == 'CategoryExternalId':
		try:
			category_id = returnNode(line,value,options)
			category_dict[category_id] = {
				'ExternalId': category_id,
				'Name': returnNode(line,product_map['CategoryName'],options)
			}
			return category_id
		except:
			errors += 'exception: ' + str(key) + str(line) + '\n'
			return 0
	elif key in ['Attribute', 'ModelNumber', 'ManufacturerPartNumber', 'EAN', 'UPC', 'ISBN']: # enumerates plural field types
		try:
			nodelist = returnNodeList(line,value,options)
			return nodelist
		except:
			errors += 'exception: ' + str(key) + str(value) + '\n'
			return 0
	elif key in ['Brand', 'CategoryName']: # Skip if one of these nodes is handled separately
		return 0
	else:
		return returnNode(line,value,options)

def getNode(line, productMap, options, global_map):
	return {key: checkNode(line, key, value, options, global_map,) for key, value in productMap.items()}

def generateFeed(options):
	global errors
	global brand_dict
	global category_dict
	# Access files
	clientFile = open(options.input) if options.feedtype == 'csv' else xml.dom.minidom.parse(options.input)
	clientProductFeed = open(options.output, 'w')
	if options.feedtype == 'csv':
		dialect = csv.Sniffer().sniff(clientFile.read()) 
		clientFile.seek(0) 
	reader = csv.reader(clientFile, dialect) if options.feedtype == 'csv' else clientFile.getElementsByTagName('PRODUCT')

	# Define Feed tag values
	generateDateTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
	schemaVersion = 'http://www.bazaarvoice.com/xs/PRR/ProductFeed/' + options.schema
	incrementalValue = 'false'

	# Build necessary header
	xmlPrefix = '<?xml version="1.0" encoding="UTF-8"?>'
	root = Element('Feed')
	root.set('incremental', incrementalValue)
	root.set('name', options.clientName)
	root.set('xmlns', schemaVersion)
	root.set('extractDate', generateDateTime)

	# Define top-level elements
	brands = SubElement(root, 'Brands')
	categories = SubElement(root, 'Categories')
	products = SubElement(root, 'Products')

	# Loop through input
	# This starts the iteration at row two, thereby, ignoring the first row with titles
	reader.next() if options.feedtype == 'csv' else xml.dom.minidom.parse(options.input)

	# utility
	product_Map = {}
	if options.feedtype == 'csv':
		product_Map = {
		'Name': 0,
		'ExternalId': 1,
		'ProductPageUrl': 3,
		'Description': 2,
		'ImageUrl': 4,
		'CategoryExternalId': 6,
		'CategoryName': 7,
		'Brand': 8,
		'BrandExternalId': 9
		}
	if options.feedtype == 'xml':
		product_Map = {
		'Name': 'SHORT_DESCRIPTION',
		'ExternalId': 'BASE_MODEL_NUMBER',
		'ProductPageUrl': 'MODEL_NUMBER',
		'Description': 'LONG_DESCRIPTION',
		'ImageUrl': 'IMAGE_URL',
		'CategoryName': 'CATEGORY_PATH_TEXT',
		'CategoryExternalId': 'CATEGORY_ITEM_SEQ_NO',
		'Brand': 'BRAND',
		'BrandExternalId': 'BRAND_CODE',
		'ManufacturerPartNumber': 'MODEL_SEQ_NO',
		'UPC': 'UPC',
		'ModelNumber': 'MODEL_NUMBER'
		}

	for line in reader:
		productList = {key: value for key, value in product_Map.items()} # copy map for given product
		productList = {key: value for key, value in getNode(line,productList,options,product_Map).items() if value > 0} # get mapped values for product
		
		product = SubElement(products, 'Product') # Define individual top-level elements
		elementsMapToLists = { # add product to element map, duplicate checking should happen here
				product: productList,
			}

		for key, value in elementsMapToLists.items(): # write new product, brand, and category nodes here
			for k, v in value.items():
				populateTags(key, k, v) # populate flat tags in product

	# populate brand and category nodes
	for key in brand_dict:
		brand = SubElement(brands, 'Brand')
		populateTags(brand, 'Name', brand_dict[key]['Name'])
		populateTags(brand, 'ExternalId', brand_dict[key]['ExternalId'])

	for key in category_dict:
		category = SubElement(categories, 'Category')
		populateTags(category, 'Name', category_dict[key]['Name'])
		populateTags(category, 'ExternalId', category_dict[key]['ExternalId'])

	# Format and pretty print XML
	print 'Attempting to parse and write new feed'
	root = parseString(tostring(root)).toprettyxml()
	root = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL).sub('>\g<1></', root)

	print 'Validating feed:'
	clientProductFeed.write(root)
	clientProductFeed.close()
	subprocess.call(['xmllint --schema ' + schemaVersion + ' --noout ' + options.output], shell=True)

	print errors

###################################################################
# Handle command line args
###################################################################

def main(argv):
	usage = 'usage: %prog [options] arg'
	parser = OptionParser(usage)
	parser.add_option('-c', '--clientName', help='Database name for the client', action='store', dest='clientName')
	parser.add_option('-i', '--input', help='Location of the CSV input file', action='store', dest='input')
	parser.add_option('-o', '--output', help='Location of the XML output file', action='store', dest='output')
	parser.add_option('-s', '--schema', default='5.1', help='The Bazaarvoice XML schema version', action='store', dest='schema')
	parser.add_option('-t', '--type', default='csv', help='Defaults to csv filetype, can be XML instead', action='store', dest='feedtype')

	(options, args) = parser.parse_args()

	generateFeed(options)

if __name__ == "__main__":
	main(sys.argv[1:])