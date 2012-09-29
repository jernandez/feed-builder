Instructions
============

This script ingests a CSV file and outputs an XML feed that conforms to the BV schema for product data feeds.
The XML file can then be used to populate your product content into Bazaarvoice's databases.


Files
-----

Here are the list of files in this directory:

* feed-as-csv.csv -- The CSV file with basic client product data.
* feed-as-csv-with-additonal-info.csv -- The CSV file with basic client product data and some secondary product information.
* feed-from-csv.xml -- The output of the CSV file into a Bazaarvoice-specific XML format.
* feed-from-csv-with-additonal-info.xml -- The output of the CSV file into a Bazaarvoice-specific XML format.
* feed_generator.py -- The script to transform the data.


Usage
-----

    > python feed_generator.py -c democlient -i feed-as-csv.csv -o feed-from-csv.xml -S 5.1
    > python name_of_script.py -c clientName - i location_of_input_csv -o location_of_output_xml -m moderationStatus (optional; dafaults to 'SUBMITTED'. Options: 'APPROVED' or 'SUBMITTED') -s schemaVersion (optional; defaults to '5.1')
