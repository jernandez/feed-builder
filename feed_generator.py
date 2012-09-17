#! /usr/bin/env python
import time,sys, getopt, re
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString

###################################################################
# to dos
###################################################################
# product families
# multi locales
# error checking
# accept excel files for inputs


###################################################################
# handle command line args
###################################################################

def main(argv):                         
              
    try:                                
        opts, args = getopt.getopt(argv, "hc:i:o:s:", ["help", "clientname=", "infile=", "outfile=", "schema="]) 
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)       
    for opt, arg in opts: 
    	if opt in ("-h", "--help"):
    		usage()
    		sys.exit(2)
    	elif opt in ("-c", "--clientName"):
    		global clientName
    		clientName = arg
    	elif opt in ("-i", "--infile"):
    		global infile
    		infile = arg
    	elif opt in ("-o", "--outfile"):
    		global outfile
    		outfile = arg
    	elif opt in ("-s", "--schema"):
    		global schema
    		schema = arg
    	
if __name__ == "__main__":
    main(sys.argv[1:])		

###################################################################
###################################################################



#clientName = 'bridgestone'
clientFile = open(infile)
clientProductFeed = open(outfile, 'w')
generateDateTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
schemaVersion = 'http://www.bazaarvoice.com/xs/PRR/ProductFeed/' + schema
incrementalValue = 'false'

#build necessary header
root = Element('Feed')
root.set('incremental', incrementalValue)
root.set('name', clientName)
root.set('xmlns', schemaVersion)
root.set('extractDate', generateDateTime)

# 
brands = SubElement(root, 'Brands')
categories = SubElement(root, 'Categories')
products = SubElement(root, 'Products')

#

for line in clientFile:
	vals = line.split('	')
	externalId = vals[0]
	recordType = vals[1]
	recordName = vals[2]
	productDesc = vals[3]
	productUrl = vals[4]
	imageUrl = vals[5]
	categoryId = vals[6]

	# pipe delimited values
	manufactureNums = vals[7]
	brand = vals[8]
	locale  = vals[9]
	#ISBN = vals[10]
	#EAN = vals[11]
	#UPC = vals[12]


	if recordType == 'Product':
		product = SubElement(products, 'Product')
		externalIDNode = SubElement(product, 'ExternalId')
		externalIDNode.text = externalId
		nameNode = SubElement(product, 'Name')
		nameNode.text = recordName
		descNode = SubElement(product, 'Description')
		descNode.text = productDesc
		pdpURLNode = SubElement(product, 'ProductPageUrl')
		pdpURLNode.text = productUrl
		imageNode = SubElement(product, 'ImageUrl')
		imageNode.text = imageUrl
	elif recordType == 'category':
		category = SubElement(categories, 'Category')
		externalIDNode = SubElement(category, 'ExternalId')
		externalIDNode.text = externalId
		nameNode = SubElement(category, 'Name')
		nameNode.text = recordName
		pdpURLNode = SubElement(category, 'CategoryPageUrl')
		pdpURLNode.text = productUrl
		if categoryId != externalId:
			parentCatNode = SubElement(category, 'ParentExternalId')
			parentCatNode.text = categoryId
	#elif recordType == 'brand':
	#	brand = SubElement(brands, 'Brand')
	#	externalIDNode = SubElement(brand, 'ExternalId')
	#	externalIDNode.text = externalId
	#	nameNode = SubElement(brand, 'Name')
	#	nameNode.text = recordName
		
clientProductFeed.write(tostring(root))
