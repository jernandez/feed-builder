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

#products = SubElement(root, 'Products')

uniqueId = 99999

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
	qCount = 4
	aCount = 4
	#positions where question/answers start in spreadsheet
	qPos = 1
	aPos = 2
		

	# pipe delimited values

	product = SubElement(root, 'Product')
	product.set('id', externalId)
	externalIDNode = SubElement(product, 'ExternalId')
	externalIDNode.text = externalId
	numQuestionsNode = SubElement(product, 'NumQuestions')
	numQuestionsNode.text = str(qCount)
	numAnswersNode = SubElement(product, 'NumAnswers')
	numAnswersNode.text = str(aCount)
	questions = SubElement(product, 'Questions')

	for i in range(0, qCount):
		#Question1
		questionNode = SubElement(questions, 'Question')
		questionNode.set('id', str(uniqueId))
		uniqueId += 1
		#question
		questionSummary = SubElement(questionNode, 'QuestionSummary')
		questionSummary.text = vals[qPos]
		questionDetails = SubElement(questionNode, 'QuestionDetails')
		questionDetails.text = vals[qPos]
		#asker profile information
		userNicknameNode = SubElement(questionNode, 'UserNickname')
		userNicknameNode.text = "Customer Help"	
		
		questionUserProfileNode = SubElement(questionNode, 'UserProfileReference')
		profileExternalID = SubElement(questionUserProfileNode, 'ExternalId')
		profileExternalID.text = "storagecom"
		anonymous = SubElement(questionUserProfileNode, 'Anonymous')
		anonymous.text = "false"
		hyperlinkingNode = SubElement(questionUserProfileNode, 'HyperlinkingEnabled')
		hyperlinkingNode.text = "false"
		#answer 
		allAnswersNode = SubElement(questionNode, "Answers")
		answerNode = SubElement(allAnswersNode, "Answer")
		answerNode.set('id', str(uniqueId))
		uniqueId += 1
		answerSummary = SubElement(answerNode, "AnswerText")
		answerSummary.text = vals[aPos]
		answerUserNicknameNode = SubElement(answerNode, 'UserNickname')
		answerUserNicknameNode.text = "Customer Help"	
		answerUserProfileNode = SubElement(answerNode, 'UserProfileReference')
		profileExternalID = SubElement(answerUserProfileNode, 'ExternalId')
		profileExternalID.text = "storagecom"
		hyperlinkingNode = SubElement(answerUserProfileNode, 'HyperlinkingEnabled')
		hyperlinkingNode.text = "false"
		anonymous = SubElement(answerUserProfileNode, 'Anonymous')
		anonymous.text = "false"
		qPos += 2
		aPos += 2
		
clientProductFeed.write(tostring(root))
#print tostring(root)