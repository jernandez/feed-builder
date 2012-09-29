#! /usr/bin/env python
import time, sys, csv
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
		line[num]
		return True
	except IndexError:
		print errorMsg

def generateFeed(options):
	# Access files
	clientFile = open(options.input)
	clientProductFeed = open(options.output, 'w')
	dialect = csv.Sniffer().sniff(clientFile.read(1024))
	clientFile.seek(0)
	reader = csv.reader(clientFile, dialect)

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
	reader.next() # This starts the iteration at row two, thereby, ignoring the first row with titles
	for line in reader:
		productName = line[0]
		productId = line[1]
		productDesc = line[2]
		productPageUrl = line[3]
		productImageUrl = line[4]
		categoryName = line[5]
		categoryId = line[6]
		brandName = line[7]
		brandId = line[8]

		# Define individual top-level elements
		product = SubElement(products, 'Product')
		category = SubElement(categories, 'Category')
		brand = SubElement(brands, 'Brand')

		# Secondary product information (mfg. part no, UPC, model no., etc.)
		if checkForExistence(line, 9, 'Secondary product information is missing (Mfg. Part Number)'):
			mfgPartNumbers = SubElement(product, 'ManufacturerPartNumbers')
			populateTags(mfgPartNumbers, 'ManufacturerPartNumber', line[9])
		if checkForExistence(line, 10, 'Secondary product information is missing (UPC)'):
			upcs = SubElement(product, 'UPCs')
			populateTags(upcs, 'UPC', line[10])
		if checkForExistence(line, 11, 'Secondary product information is missing (Model Number)'):
			modelNumbers = SubElement(product, 'ModelNumbers')
			populateTags(modelNumbers, 'ModelNumber', line[11])

		# Product families
		if checkForExistence(line, 12, 'Product families information is missing'):
			if line[12] != '':
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

		# Define lists
		productList = {
			'Name': productName, 
			'ExternalId': productId,
			'Description': productDesc,
			'ProductPageUrl': productPageUrl,
			'ImageUrl': productImageUrl,
			'CategoryExternalId': categoryId,
			'BrandExternalId': brandId
		}

		categoryList = {
			'Name': categoryName, 
			'ExternalId': categoryId
		}

		brandList = {
			'Name': brandName, 
			'ExternalId': brandId
		}

		elementsMapToLists = {
			product: productList,
			category: categoryList,
			brand: brandList
		}

		for key, value in elementsMapToLists.items():
			for k, v in value.items():
				populateTags(key, k, v)

	clientProductFeed.write(xmlPrefix)
	clientProductFeed.write(tostring(root))

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
	
	(options, args) = parser.parse_args()

	generateFeed(options)

if __name__ == "__main__":
    main(sys.argv[1:])	





