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
        opts, args = getopt.getopt(argv, "hc:i:o:s:v:", ["help", "clientname=", "infile=", "outfile=", "schema=", "incrementalValue="]) 
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
    	elif opt in ("-v", "--incrementalValue"):
    		global incrementalValue
    		incrementalValue = arg

    	
if __name__ == "__main__":
    main(sys.argv[1:])		

###################################################################
###################################################################



#clientName = 'bridgestone'
clientFile = open(infile)
clientProductFeed = open(outfile, 'w')
generateDateTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
schemaVersion = 'http://www.bazaarvoice.com/xs/PRR/StandardClientFeed/' + schema

#build necessary header
root = Element('Feed')
#root.set('incremental', incrementalValue)
root.set('name', clientName)
root.set('xmlns', schemaVersion)
root.set('extractDate', generateDateTime)

# 

#products = SubElement(root, 'Products')


for line in clientFile:
	vals = line.split('	')
	externalId = vals[0]
	question1 = vals[1]
	answer1 = vals[2]
	question2 = vals[3]
	answer2 = vals[4]
	question3 = vals[5]
	answer3 = vals[6]
	question4 = vals[7]
	answer4 = vals[8]

	# pipe delimited values

	product = SubElement(root, 'Product')
	product.set('id', externalId)
	externalIDNode = SubElement(product, 'ExternalId')
	externalIDNode.text = externalId
	numQuestionsNode = SubElement(product, 'NumQuestions')
	numQuestionsNode.text = '4'
	numAnswersNode = SubElement(product, 'NumAnswers')
	numAnswersNode.text = '4'
	questions = SubElement(product, 'Questions')
	question1Node = SubElement(questions, 'Question')
	#asker profile information
	questionUserProfileNode = SubElement(question1Node, 'UserProfileReference')
	profileExternalID = SubElement(questionUserProfileNode, 'ExternalId')
	profileExternalID.text = "12345"
	anonymous = SubElement(questionUserProfileNode, 'Anonymous')
	anonymous.text = "true"
	hyperlinkingNode = SubElement(questionUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	#questions
	question1Summary = SubElement(question1Node, 'QuestionSummary')
	question1Summary.text = question1
	#answers
	allAnswers1Node = SubElement(question1Node, "Answers")
	answer1Node = SubElement(allAnswers1Node, "Answer")
	answer1Summary = SubElement(answer1Node, "AnswerText")
	answer1Summary.text = answer1
	answerUserProfileNode = SubElement(answer1Node, 'UserProfileReference')
	profileExternalID = SubElement(answerUserProfileNode, 'ExternalId')
	profileExternalID.text = "xyz322"
	hyperlinkingNode = SubElement(answerUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	anonymous = SubElement(answerUserProfileNode, 'Anonymous')
	anonymous.text = "false"

		
clientProductFeed.write(tostring(root))