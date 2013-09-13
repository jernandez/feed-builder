Instructions
============

This script ingests a CSV file and outputs an XML feed that conforms to the BV schema for product data feeds.
The XML file can then be used to populate your product content into Bazaarvoice's databases.


Files
-----

Here is the list of files in this directory:

* feed-as-csv.csv -- The CSV file with basic client product data.
* mapping.py -- This file contains the list of fields and the column order
* feed_generator.py -- The script to transform the data.

Options
-----
To get a full list of options, type: 
	> python feed_generator.py --help

The available options are: 
* -i or --input: path to the csv file you will need to use for import
* -o or --output: path to the product feed which will be generated from teh script
* -c or --client: databasename of the client
* -l or --locale: default locale of the feed

Usage
-----

    > python feed_generator.py -c democlient -i feed-as-csv.csv -o feed-from-csv.xml 
    > python feed_generator.py -c democlient -i feed-as-csv-with-additonal-info.csv -o feed-from-csv-with-additonal-info.xml 
    