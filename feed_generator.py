#! /usr/bin/env python
import time, sys, csv, xml, re, subprocess
import logging
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from optparse import OptionParser
import mapping

###################################################################
# Nuts and bolts
###################################################################
# Global error log
errors = ''
# Global declarations
brand_dict = {}
category_dict = {}
product_dict = {}
productMap = {}
_nodeVariants = ['Name',  'ProductPageUrl', 'Description', 'ImageUrl', 'CategoryPageUrl']

def populateTags(parentTag, _dict):
	#
	for k, v in _dict.items():

		if k[:-1] in _nodeVariants: #if the key(minus the 's') is one of the locale variants
		
			node = SubElement(parentTag, k) #create a subnode to store all the values

			for _lv in v: #for every locale variant, add the corresponding node
				for _k in _lv.keys(): 
					subNode = SubElement(node, k[:-1])
					subNode.set('locale', _k) 
					subNode.text = _lv[_k]

		elif isinstance(v, list):
			node = SubElement(parentTag, k +'s')
			for item in v:
				subNode = SubElement(node, k)
				subNode.text = item
		
		elif v:
			node = SubElement(parentTag, k)
			node.text = v

def localify(_pdict, options, _type):
	'''
	this will take all the locale specific product dicts and will consolidate into one multi-locale dict
	'''
	_dict = {}

	#setting up the default product dict, ignoring the locale definition
	if _type == 'product':

		_variants = ['Name', 'ProductPageUrl', 'Description', 'ImageUrl']

	elif _type == 'brand': 
		_variants = ['Name']
		
	elif _type == 'category':
		_variants = ['Name', 'CategoryPageUrl', 'ImageUrl']
	
	for k, v in _pdict[options.locale].items():

		if k == 'CategoryParentExternalId':
			k = 'ParentExternalId'

		elif k!= 'locale':
			_dict[k] = v

	for _lv in _variants: #for every locale variant

		_localeVariantList = [] #store all the locale variants as a list of dicts

		for l, p in _pdict.items(): #for every locale specific node value
			
			_lang, _locale = l.split('_') #ensure the locale is in the proper format
			l = _lang.lower() + '_' + _locale.upper()

			_locale_pdict = {l : p[_lv]} # create a temporary dict with the locale/value
			_localeVariantList.append(_locale_pdict) # store the dict in the list

		_dict[_lv+'s'] = _localeVariantList # set the locale variant to the list just populated

	return _dict

def returnNode(line, value, options, xmlIndex=0):
	try:
		return line[value]
	except:
		errors += '\nMissing: ' + str(value) + ': Line ' + str(line)
		return 0

def returnNodeList(line, value, options):
	global errors
	try:
		return [item for item in returnNode(line,value,options).split('|')]
	except:
		return 0

def checkNode(line, key, value, options, product_map):
	if key == 'BrandExternalId':
		try:
			brand_id = returnNode(line,product_map['BrandExternalId'],options)
			locale = returnNode(line,product_map['locale'],options)
			
			if brand_id not in brand_dict: 
				brand_dict[brand_id] = {}

			brand_dict[brand_id][locale] = 	{
				'Name': returnNode(line,product_map['Brand'],options),
				'ExternalId' : brand_id
			}

			return brand_id
		except:
			errors += '\nexception: ' + str(key) + str(line)
			return 0
	elif key == 'CategoryExternalId':
		try:
			category_id = returnNode(line,product_map['CategoryExternalId'],options)
			locale = returnNode(line,product_map['locale'],options)

			if category_id not in category_dict:
				category_dict[category_id] = {}

			category_dict[category_id][locale] = {
				'Name': returnNode(line,product_map['CategoryName'],options),
				'ExternalId': category_id,
				'CategoryPageUrl': returnNode(line,product_map['CategoryPageUrl'],options),
				'CategoryParentExternalId': returnNode(line,product_map['CategoryParentExternalId'],options),
				'ImageUrl': returnNode(line,product_map['CategoryImageUrl'],options)
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
			errors += '\nexception: ' + str(key) + str(value) + '\n'
			return 0
	elif key in ['Brand', 'CategoryName', 'CategoryPageUrl', 'CategoryImageUrl', 'CategoryParentExternalId']: # Skip if one of these nodes is handled separately
	 	return 0
	else:
		return returnNode(line,value,options)
		
def getNode(line, productMap, options, global_map):
	return {key: checkNode(line, key, value, options, global_map) for key, value in productMap.items()}

def generateFeed(options):
	global errors
	global brand_dict
	global category_dict
	global product_dict

	# Access files
	clientFile = open(options.input)
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
	reader.next()

	# utility
	product_Map = mapping.returnMap()

	for line in reader:
		productList = {key: value for key, value in product_Map.items()} # copy map for given product
		productList = {key: value for key, value in getNode(line,productList,options,product_Map).items() if value > 0} # get mapped values for product
		
		#add the product to product_dict keyed off external id so we can account for multiple locales
		if productList['ExternalId'] not in product_dict:
			product_dict[productList['ExternalId']] = {}

 	 	product_dict[productList['ExternalId']][productList['locale']] = productList # externalId: locale : productList
 
	for externalId, locale in product_dict.items(): # write new product, brand, and category nodes here
		if externalId != '':
			product = SubElement(products, 'Product') # Define individual top-level elements
			populateTags(product, localify(product_dict[externalId], options, 'product'))

	for externalId, locale in brand_dict.items(): 
		if externalId != '':
			brand = SubElement(brands, 'Brand')
			populateTags(brand, localify(brand_dict[externalId], options, 'brand'))

	for externalId, locale in category_dict.items():
		if externalId != '':
			category = SubElement(categories, 'Category')
			populateTags(category, localify(category_dict[externalId], options, 'category'))

	# Format and pretty print XML
	print 'Attempting to parse and write new feed'
	root = parseString(tostring(root)).toprettyxml()
	root = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL).sub('>\g<1></', root)

	print 'Validating feed:'
	clientProductFeed.write(root)
	clientProductFeed.close()
	subprocess.call(['xmllint --schema ' + schemaVersion + ' --noout ' + options.output], shell=True)

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
	parser.add_option('-l', '--locale', help='The default locale for this product feed -- needs to be set regardless if this is a multi-locale feed or not', action='store', dest='locale')


	(options, args) = parser.parse_args()

	generateFeed(options)

if __name__ == "__main__":
	main(sys.argv[1:])