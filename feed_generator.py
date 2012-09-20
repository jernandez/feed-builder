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
	#Question1
	question1Node = SubElement(questions, 'Question')
	#asker profile information
	questionUserProfileNode = SubElement(question1Node, 'UserProfileReference')
	profileExternalID = SubElement(questionUserProfileNode, 'ExternalId')
	profileExternalID.text = "12345"
	anonymous = SubElement(questionUserProfileNode, 'Anonymous')
	anonymous.text = "true"
	hyperlinkingNode = SubElement(questionUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	#questions 1
	question1Summary = SubElement(question1Node, 'QuestionSummary')
	question1Summary.text = question1
	#answer 1
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

		#Question2
	question2Node = SubElement(questions, 'Question')
	#asker profile information
	questionUserProfileNode = SubElement(question2Node, 'UserProfileReference')
	profileExternalID = SubElement(questionUserProfileNode, 'ExternalId')
	profileExternalID.text = "22345"
	anonymous = SubElement(questionUserProfileNode, 'Anonymous')
	anonymous.text = "true"
	hyperlinkingNode = SubElement(questionUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	#questions 2
	question2Summary = SubElement(question2Node, 'QuestionSummary')
	question2Summary.text = question2
	#answer 2
	allAnswers2Node = SubElement(question2Node, "Answers")
	answer2Node = SubElement(allAnswers2Node, "Answer")
	answer2Summary = SubElement(answer2Node, "AnswerText")
	answer2Summary.text = answer2
	answerUserProfileNode = SubElement(answer2Node, 'UserProfileReference')
	profileExternalID = SubElement(answerUserProfileNode, 'ExternalId')
	profileExternalID.text = "xyz322"
	hyperlinkingNode = SubElement(answerUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	anonymous = SubElement(answerUserProfileNode, 'Anonymous')
	anonymous.text = "false"

		#Question1
	question3Node = SubElement(questions, 'Question')
	#asker profile information
	questionUserProfileNode = SubElement(question3Node, 'UserProfileReference')
	profileExternalID = SubElement(questionUserProfileNode, 'ExternalId')
	profileExternalID.text = "33345"
	anonymous = SubElement(questionUserProfileNode, 'Anonymous')
	anonymous.text = "true"
	hyperlinkingNode = SubElement(questionUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	#questions 3
	question3Summary = SubElement(question3Node, 'QuestionSummary')
	question3Summary.text = question3
	#answer 3
	allAnswers3Node = SubElement(question3Node, "Answers")
	answer3Node = SubElement(allAnswers3Node, "Answer")
	answer3Summary = SubElement(answer3Node, "AnswerText")
	answer3Summary.text = answer3
	answerUserProfileNode = SubElement(answer3Node, 'UserProfileReference')
	profileExternalID = SubElement(answerUserProfileNode, 'ExternalId')
	profileExternalID.text = "xyz333"
	hyperlinkingNode = SubElement(answerUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	anonymous = SubElement(answerUserProfileNode, 'Anonymous')
	anonymous.text = "false"

		#Question4
	question4Node = SubElement(questions, 'Question')
	#asker profile information
	questionUserProfileNode = SubElement(question4Node, 'UserProfileReference')
	profileExternalID = SubElement(questionUserProfileNode, 'ExternalId')
	profileExternalID.text = "42345"
	anonymous = SubElement(questionUserProfileNode, 'Anonymous')
	anonymous.text = "true"
	hyperlinkingNode = SubElement(questionUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	#questions 4
	question4Summary = SubElement(question4Node, 'QuestionSummary')
	question4Summary.text = question4
	#answer 4
	allAnswers4Node = SubElement(question4Node, "Answers")
	answer4Node = SubElement(allAnswers4Node, "Answer")
	answer4Summary = SubElement(answer4Node, "AnswerText")
	answer4Summary.text = answer4
	answerUserProfileNode = SubElement(answer4Node, 'UserProfileReference')
	profileExternalID = SubElement(answerUserProfileNode, 'ExternalId')
	profileExternalID.text = "xyz322"
	hyperlinkingNode = SubElement(answerUserProfileNode, 'HyperlinkingEnabled')
	hyperlinkingNode.text = "false"
	anonymous = SubElement(answerUserProfileNode, 'Anonymous')
	anonymous.text = "false"

		
clientProductFeed.write(tostring(root))