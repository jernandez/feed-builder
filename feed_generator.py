#! /usr/bin/env python
import time, sys, csv, xml, re
import logging
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from optparse import OptionParser

###################################################################
# Nuts and bolts
###################################################################
def populateTags(parentTag, tagTitle, tagText):
	node = SubElement(parentTag, tagTitle)
	node.text = tagText

def checkForExistence(parentTag, indKey, keyDesc, errorMsg):
	try:
		for item in indKey[keyDesc].split('|'):
			node = SubElement(parentTag, keyDesc)
			node.text = item
			if item == '':
				logging.error(errorMsg)
				print indKey
	except IndexError:
		print 'Index Error'
def checkForExistenceMinor(rootParent, indKey, keyDesc, errorMsg):
	try:
		if indKey[keyDesc] != '':
			keyName = keyDesc+'s'
			productChild = SubElement(rootParent, keyName)
			for item in indKey[keyDesc].split('|'):
				node = SubElement(productChild, keyDesc)
				node.text = item
			if keyDesc == 'UPC':
				if len(item) != 12:
					logging.error('A UPC must be 12 characters in length')
					print item
	except IndexError:
		print 'Index Error'
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
	product_dict = {}
	brand_dict = {}
	category_dict = {}
	product_Map = {}
	# if options.feedtype == 'csv':
	# 	product_Map = {
	# 	'Name': 0,
	# 	'ExternalId': 1,
	# 	'ProductPageUrl': 3,
	# 	'Description': 2,
	# 	'ImageUrl': 4,
	# 	'CategoryExternalId': 6,
	# 	}

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
	primary_product_fields = [
		'Name',
		'ExternalId',
		'ProductPageUrl',
		'Description',
		'ImageUrl',
		'CategoryExternalId']


	for line in reader:
		# productList = {key: value for key, value in product_Map.items() if key in primary_product_fields}
		if options.feedtype == 'xml':
			productList = {key: value for key, value in getXMLValues(line,productList).items() if value > 0}

		# Define individual top-level elements
		product = SubElement(products, 'Product')

		# Secondary product information (mfg. part no, UPC, model no., etc.)
		if options.feedtype == 'csv':
			if product_ids.get(line[1], False):
				logging.error('Duplicate product id: This product has been omitted from the feed.')
				print line
				continue
			product_ids[line[1]] = True

			product_dict[line[1]] = {
				'ExternalId': line[1],
				'Name': line[0],
				'Description': line[2],
				'CategoryExternalId': line[6],
				'ProductPageUrl': line[3],
				'ImageUrl': line[4],
				'BrandExternalId': line[7],
				'ManufacturerPartNumber': line[9],
				'UPC': line[10],
				'ModelNumber': line[11]
				# 'EAN': line[12]
			}
			brand_dict[line[8]]= {
				'ExternalId': line[8],
				'Name': line[7]
			}
			category_dict[line[6]]={
				'ExternalId': line[6],
			 	'Name': line[5]
			}

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
	if options.feedtype == 'xml':	
		for key in brand_dict:
			brand = SubElement(brands, 'Brand')
			populateTags(brand, 'Name', brand_dict[key]['Name'])
			populateTags(brand, 'ExternalId', brand_dict[key]['ExternalId'])

		for key in category_dict:
			category = SubElement(categories, 'Category')
			populateTags(category, 'Name', category_dict[key]['Name'])
			populateTags(category, 'ExternalId', category_dict[key]['ExternalId'])


	for key in brand_dict:
		brand = SubElement(brands, 'Brand')
		brandKey = brand_dict[key]
		checkForExistenceMinor(brand, brandKey, 'Name', 'Brand name is missing for')
		checkForExistenceMinor(brand, brandKey, 'ExternalId', 'Brand external id is missing for')

	for key in category_dict:
		category = SubElement(categories, 'Category')
		catKey = category_dict[key]
		checkForExistence(category, catKey, 'Name', 'Category name is missing for')
		checkForExistence(category, catKey, 'ExternalId', 'Category external id is missing for ')
	
	for key in product_dict:
		product = SubElement(products, 'Product')
		prodKey = product_dict[key]
		checkForExistence(product, prodKey, 'ExternalId', 'Product External ID is missing for')
		checkForExistence(product, prodKey, 'Name', 'Product Name is missing for ')
		checkForExistenceMinor(product, prodKey, 'Description', 'Product Description is missing for ')
		checkForExistence(product, prodKey, 'CategoryExternalId', 'Category External Id is missing for ')
		checkForExistence(product, prodKey, 'ProductPageUrl', 'Product page URL is missing for ')
		checkForExistence(product, prodKey, 'ImageUrl', 'Image URL is missing for ')
		checkForExistence(product, prodKey, 'BrandExternalId', 'Brand external Id is missing for ')
		checkForExistenceMinor(product, prodKey, 'ManufacturerPartNumber', 'Manufacturer Part Number is missing for ')
		checkForExistenceMinor(product, prodKey, 'UPC', 'UPC is missing for ')
		checkForExistenceMinor(product, prodKey, 'ModelNumber', 'Model Number is missing for')

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