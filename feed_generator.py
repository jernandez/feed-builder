#! /usr/bin/env python
import time,sys, getopt, pymongo, re
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from pymongo import Connection


'''
	product_id = #apihostname.find({}, {_id:1,client:1})  id is the apihostname, client is the externalid
	productName = #sites.find({}, {_client._name:1})
	productDesc = #sites.find({}, {_client._name:1})
	productUrl = #apihostname.find({}, {_id:1,client:1,_clientDomainNames:1})  id is the apihostname, client is the externalid
	imageUrl = #concatenate apihostname+static+_customerLogoImageName sites.find({}, {_client._name:1,_customerLogoImageName:1})
'''

###################################################################
# handle command line args
###################################################################

def main(argv):                         
              
    try:                                
        opts, args = getopt.getopt(argv, "h:o:s:", ["help", "outfile=", "schema="]) 
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)       
    for opt, arg in opts: 
    	if opt in ("-h", "--help"):
    		usage()
    		sys.exit(2)
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



#open connection to mongodb
connection=Connection('qaclientconfigstore.lab', 27017)
db=connection.configs

clientProductFeed = open(outfile, 'w')
generateDateTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
schemaVersion = 'http://www.bazaarvoice.com/xs/PRR/ProductFeed/' + schema
incrementalValue = 'false'

#build necessary header
root = Element('Feed')
root.set('incremental', incrementalValue)
root.set('name', 'bazaarvoice')
root.set('xmlns', schemaVersion)
root.set('extractDate', generateDateTime)

products = SubElement(root, 'Products')

#query database for client name, logo name, and domain name
clients=list(db.sites.find({}, {'_displayCodeKey':1,'_client._name':1,'_clientDomainNames':1}).skip(0).limit(100))
for row in clients:
	product_id = row['_client']['_name']
	productName = row['_client']['_name']
	productDesc = row['_client']['_name']
	productUrl = 'http://'+row['_clientDomainNames'][0]
	imageUrl = 'http://'+row['_client']['_name']+'.ugc.bazaarvoice.com/static/'+row['_displayCodeKey']+'/logo.gif'
	product = SubElement(products, 'Product')
	externalIDNode = SubElement(product, 'ExternalId')
	externalIDNode.text = product_id
	nameNode = SubElement(product, 'Name')
	nameNode.text = productName
	descNode = SubElement(product, 'Description')
	descNode.text = productDesc
	pdpURLNode = SubElement(product, 'ProductPageUrl')
	pdpURLNode.text = productUrl
	imageNode = SubElement(product, 'ImageUrl')
	imageNode.text = imageUrl

#pretty prints the xml and writes to file
clientProductFeed.write(parseString(tostring(root)).toprettyxml())
