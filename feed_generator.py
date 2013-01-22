#! /usr/bin/env python
import time, sys, csv, xml, re
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from optparse import OptionParser

###################################################################
# Nuts and bolts
###################################################################
def populateTags(parentTag, tagTitle, tagText):
	node = SubElement(parentTag, tagTitle)
	node.text = tagText

def checkForExistence(line, num, errorMsg):
	try: 
		if line[num] == '':
			print errorMsg
			return False
		return True			
	except IndexError:
		print errorMsg

def checkXMLNode(line, attributeNode, errorMsg):
	try:
		return line.getElementsByTagName(attributeNode)[0].firstChild.nodeValue
	except:
		print errorMsg
		return 0

def getXMLValues(line, productMap):
	return {key: checkXMLNode(line,value,(str(key)+' not found')) for key, value in productMap.items()}

def generateFeed(options):
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
	product_ids = {}
	brand_dict = {}
	category_dict = {}
	product_Map = {}
	if options.feedtype == 'csv':
		product_Map = {
		'Name': 0,
		'ExternalId': 1,
		'ProductPageUrl': 3,
		'Description': 2,
		'ImageUrl': 4,
		'CategoryExternalId': 6
		}
	elif options.feedtype == 'xml':
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
	primary_product_fields = [
		'Name',
		'ExternalId',
		'ProductPageUrl',
		'Description',
		'ImageUrl',
		'CategoryExternalId']


	for line in reader:
		productList = {key: value for key, value in product_Map.items() if key in primary_product_fields}
		if options.feedtype == 'csv':
			productList = {key: line[value] for key, value in productList.items()}
		elif options.feedtype == 'xml':
			productList = {key: value for key, value in getXMLValues(line,productList).items() if value > 0}

		# Define individual top-level elements
		product = SubElement(products, 'Product')

		# Secondary product information (mfg. part no, UPC, model no., etc.)
		if options.feedtype == 'csv':
			if checkForExistence(line, 7, 'Brand information is missing'):
				brand_dict[line[8]] = {
					'ExternalId': line[8],
					'Name': line[7]
				}
				populateTags(product, 'BrandExternalId', line[8])
			if checkForExistence(line, 5, 'Category information is missing'):
				category_dict[line[6]] = {
					'ExternalId': line[6],
					'Name': line[5]
				}
			if checkForExistence(line, 9, 'Secondary product information is missing (Mfg. Part Number)'):
				mfgPartNumbers = SubElement(product, 'ManufacturerPartNumbers')
				for mfgPartNumber in line[9].split('|'):
					populateTags(mfgPartNumbers, 'ManufacturerPartNumber', mfgPartNumber)
			if checkForExistence(line, 10, 'Secondary product information is missing (UPC)'):
				upcs = SubElement(product, 'UPCs')
				populateTags(upcs, 'UPC', line[10])
			if checkForExistence(line, 11, 'Secondary product information is missing (Model Number)'):
				modelNumbers = SubElement(product, 'ModelNumbers')
				for modelNumber in line[11].split(':'):
					populateTags(modelNumbers, 'ModelNumber', modelNumber)
			# Product families
			if checkForExistence(line, 12, 'Product families information is missing'):
				attrs = SubElement(product, 'Attributes')
				familyAttr = SubElement(attrs, 'Attribute')
				familyAttr.set('id', 'BV_FE_FAMILY')
				familyValue = SubElement(familyAttr, 'Value')
				familyValue.text = line[12]
				# Expand product families
				if checkForExistence(line, 13, ''):
					if line[13] != '':
						expandAttr = SubElement(attrs, 'Attribute')
						expandAttr.set('id', 'BV_FE_EXPAND')
						expandValue = SubElement(expandAttr, 'Value')
						expandValue.text = 'BV_FE_FAMILY:' + line[12]
		elif options.feedtype == 'xml':
			# Brand nodes
			brandName = checkXMLNode(line, product_Map['Brand'], 'Brand ID is missing') if 'Brand' in product_Map.keys() else 0
			brandId = checkXMLNode(line, product_Map['BrandExternalId'], 'Brand name is missing') if 'BrandExternalId' in product_Map.keys() else 0
			if brandId and brandName:
				brand_dict[brandId] = {
					'ExternalId': brandId,
					'Name': brandName
				}
				populateTags(product, 'BrandExternalId', brandId)
			# Category nodes
			categoryName = checkXMLNode(line, product_Map['CategoryName'], 'Category ID is missing') if 'CategoryName' in product_Map.keys() else 0
			categoryId = checkXMLNode(line, product_Map['CategoryExternalId'], 'Category name is missing') if 'CategoryExternalId' in product_Map.keys() else 0
			if categoryId and categoryName:
				category_dict[categoryId] = {
					'ExternalId': categoryId,
					'Name': categoryName
				}
			# Manufacturer Part Numbers
			mfgPartNumber = checkXMLNode(line, product_Map['ManufacturerPartNumber'], 'ManufacturerPartNumber is missing') if 'ManufacturerPartNumber' in product_Map.keys() else 0
			if mfgPartNumber:
				mfgPartNumbers = SubElement(product, 'ManufacturerPartNumbers')
				populateTags(mfgPartNumbers, 'ManufacturerPartNumber', mfgPartNumber)
			# UPCs  TODO: if less than 6, add 0's until it's 6.  if less than 12 and greater than 6, add 0's until it's 12.
			upc = checkXMLNode(line, product_Map['UPC'], 'UPC is missing') if 'UPC' in product_Map.keys() else 0
			if upc:
				upcs = SubElement(product, 'UPCs')
				populateTags(upcs, 'UPC', upc)
			# Model Numbers
			modelNumber = checkXMLNode(line, product_Map['ModelNumber'], 'Model number is missing') if 'ModelNumber' in product_Map.keys() else 0
			if modelNumber:
				modelNumbers = SubElement(product, 'ModelNumbers')
				populateTags(modelNumbers, 'ModelNumber', modelNumber)
			# Product families
			family = checkXMLNode(line, product_Map['BV_FE_FAMILY'], 'Family is missing') if 'BV_FE_FAMILY' in product_Map.keys() else 0
			if family:
				attrs = SubElement(product, 'Attributes')
				familyAttr = SubElement(attrs, 'Attribute')
				familyAttr.set('id', 'BV_FE_FAMILY')
				familyValue = SubElement(familyAttr, 'Value')
				familyValue.text = family

		elementsMapToLists = {
			product: productList,
		}

		for key, value in elementsMapToLists.items():
			for k, v in value.items():
				populateTags(key, k, v)
		
	for key in brand_dict:
		brand = SubElement(brands, 'Brand')
		populateTags(brand, 'Name', brand_dict[key]['Name'])
		populateTags(brand, 'ExternalId', brand_dict[key]['ExternalId'])

	for key in category_dict:
		category = SubElement(categories, 'Category')
		populateTags(category, 'Name', category_dict[key]['Name'])
		populateTags(category, 'ExternalId', category_dict[key]['ExternalId'])

	# Format and pretty print XML
	root = parseString(tostring(root)).toprettyxml()
	root = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL).sub('>\g<1></', root)

	clientProductFeed.write(root)

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