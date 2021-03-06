#!/usr/bin/python

# Import necessary modules
import string
import nltk
from nltk import FreqDist
from nltk.util import ngrams
from nltk.corpus import brown

# Function to return the character left of a given character
# (Kind of cumbersome, but serves its purpose)
def leftOf(char):
  if char=='q' or char=='a' or char=='z': return False
  if char=='w': return 'q'
  if char=='e': return 'w'
  if char=='r': return 'e'
  if char=='t': return 'r'
  if char=='y': return 't'
  if char=='u': return 'y'
  if char=='i': return 'u'
  if char=='o': return 'i'
  if char=='p': return 'o'
  if char=='s': return 'a'
  if char=='d': return 's'
  if char=='f': return 'd'
  if char=='g': return 'f'
  if char=='h': return 'g'
  if char=='j': return 'h'
  if char=='k': return 'j'
  if char=='l': return 'k'
  if char=='x': return 'z'
  if char=='c': return 'x'
  if char=='v': return 'c'
  if char=='b': return 'v'
  if char=='n': return 'b'
  if char=='m': return 'n'

# Similar to above, for right of given character
def rightOf(char):
  if char=='p' or char=='l' or char=='m': return False
  if char=='q': return 'w'
  if char=='w': return 'e'
  if char=='e': return 'r'
  if char=='r': return 't'
  if char=='t': return 'y'
  if char=='y': return 'u'
  if char=='u': return 'i'
  if char=='i': return 'o'
  if char=='o': return 'p'
  if char=='a': return 's'
  if char=='s': return 'd'
  if char=='d': return 'f'
  if char=='f': return 'g'
  if char=='g': return 'h'
  if char=='h': return 'j'
  if char=='j': return 'k'
  if char=='k': return 'l'
  if char=='z': return 'x'
  if char=='x': return 'c'
  if char=='c': return 'v'
  if char=='v': return 'b'
  if char=='b': return 'n'
  if char=='n': return 'm'

# Function that performs k-fold cross validation on a dataset, with training and test functions
# I looked for a pre-made package with this, but couldn't find a good one, so added it
def kFoldCrossValidation(dataset,train,test,k,n):
  results = []
  datasetLength = len(dataset)
  sampleLength = datasetLength/k
  
  for i in range(k):
    print('Trial %d of %d:' % (i+1, k))
    trainData = dataset[:i*sampleLength] + dataset[(i+1)*sampleLength:]
    testData = dataset[i*sampleLength:(i+1)*sampleLength]
    bgramprobs = train(trainData,n)
    sRate = test(testData,bgramprobs)
    results.append(sRate)
  
  return sum(results)/len(results)

# Function to parse the data as words only consisting of lowercase letters
def stripDataset(data):
  strippedData = []
  punct = string.punctuation.replace("'","").replace("-","")
  
  print('Importing data...')
  for word in data:
    strippedWord = word.strip(string.punctuation + string.digits)
    noPunct = True
    for char in (string.digits + punct):
      if char in word:
        noPunct = False
    if len(strippedWord) > 0 and noPunct:
      strippedData.append(strippedWord.lower())
  
  return strippedData

# Train the model from the dataset
def train(dataset,n):
  listOfNGrams = []
  
  print('Extracting n-grams...')
  
  for tok in dataset:
    for i in range(1,n):
      l = ['<s>']
      for j in range(i):
        if j < len(tok):
          l.append(tok[j])
      t = tuple(l)
      listOfNGrams.append(t)
    gr = ngrams(tok,n)
    for g in gr:
      listOfNGrams.append(g)
  
  print('Calculating frequencies...')
  
  fd = FreqDist(listOfNGrams)
  probsum = 0
  
  for x in fd:
    probsum+=fd[x]
  
  # LaPlace smoothing
  numTypes=0
  
  for i in range(n):
    numTypes += 28**(i+1)
  
  bgramprobs = {}
  
  for x in fd:
    bgramprobs[x] = (float(fd[x])+1)/(float(probsum)+numTypes)
  
  bgramprobs['unseen'] = 1/numTypes
  
  return bgramprobs

# Function that returns a list of three words for consideration
def proposeCorrections(w):
  lword = w.lower()
  lastChar = lword[-1]
  
  if leftOf(lastChar):
    leftCorrection = lword[:-1] + leftOf(lastChar)
  else:
    leftCorrection = False

  if rightOf(lastChar):
    rightCorrection = lword[:-1] + rightOf(lastChar)
  else:
    rightCorrection = False
  
  options = [leftCorrection,lword,rightCorrection]
  
  return options

# Functions that calculates the probability of a word based on n-gram model of corpus
def calculateWordProb(w,bgp,n):
  if w == False: return 0
  
  wngrams = []
  
  for i in range(1,n):
    l = ['<s>']
    for j in range(i):
      l.append(w[j])
    t = tuple(l)
    wngrams.append(t)
  
  for gr in ngrams(w,n):
    wngrams.append(gr)

  prob = 1.0
  for gr in wngrams:
    if gr in bgp:
      prob*=bgp[gr]
    else:
      prob*=bgp['unseen']

  return prob

# Function that chooses the best option based on the bigram probabilities
# Here the probability of mistyping is defined
def chooseCorrection(options,bgp):
  pleft = pright = 0.2
  
  if options[0] == False:
    pright *= 1.5
  
  if options[2] == False:
    pleft *= 1.5
  
  optionProbs = [pleft,(1-pleft-pright),pright]
  
  for x in options:
    optionProbs[options.index(x)] *= calculateWordProb(x,bgp,2)
  
  maxIndex = optionProbs.index(max(optionProbs))

  return options[maxIndex]

# Function to test an individual word, from user input
# Used as a building block to testing a corpus
def testWord(w,bgp):
  options = proposeCorrections(w)
  corr = chooseCorrection(options,bgp)
  
  if corr == options[1]:
    print('No correction needed')
  else:
    print("Did you mean '%s'?" % corr)

# Function to take a single word as user input and test it
def manualTest(dataset):
  bgps = train(dataset,2)
  
  word = raw_input('Enter a word (enter q to end): ')
  while word == '':
    word = raw_input('Enter a word (enter q to end): ')
  
  while word != 'q':
    testWord(word,bgps)
    
    word = raw_input('Enter a word (enter q to end): ')
    while word == '':
      word = raw_input('Enter a word (enter q to end): ')
  
  print('Bye!')

# Function to test a dataset based on bigram probabilities
def testSet(data,bgp):
  print('Testing...')
  success = 0
  
  for word in data:
    options = proposeCorrections(word)
    corr = chooseCorrection(options,bgp)
    if corr == word:
      success+=1
  
  successRate = float(success)/float(len(data))
  return successRate

# Function that randomly changes the last character of words in the test set so that the model is not just analysing correctly typed words.
def testSetWithNoise(data,bgp):
  print('Testing...')
  success = 0
  noisyData=[]
  
  for i in range(len(data)):
    lastChar = data[i][-1]
    r = random.random()
    if leftOf(lastChar) and rightOf(lastChar):
      if r < 0.6:
        noisyData.append(data[i])
      elif r < 0.8:
        newWord = data[i][:-1] + leftOf(lastChar)
        noisyData.append(newWord)
      else:
        newWord = data[i][:-1] + rightOf(lastChar)
        noisyData.append(newWord)
    elif leftOf(lastChar):
      if r < 0.7:
        noisyData.append(data[i])
      else:
        newWord = data[i][:-1] + leftOf(lastChar)
        noisyData.append(newWord)
    else:
      if r < 0.7:
        noisyData.append(data[i])
      else:
        newWord = data[i][:-1] + rightOf(lastChar)
        noisyData.append(newWord)
  
  for i in range(len(noisyData)):
    options = proposeCorrections(noisyData[i])
    corr = chooseCorrection(options,bgp)
    if corr == data[i]:
      success+=1
  
  successRate = float(success)/float(len(data))
  return successRate

# Main function to call the rest
def main():
  dataset = stripDataset(brown.words())
  
  userChoice = raw_input('Enter 1 to run k-fold cross validation on the Brown corpus\nEnter 2 to run k-fold cross validation on the Brown corpus with noise\nEnter 3 to test a manually entered word\n(q to quit): ')
  while userChoice != '1' and userChoice != '2' and userChoice != '3' and userChoice != 'q':
    print('Please try again:')
    userChoice = raw_input('Enter 1 to run k-fold cross validation on the Brown corpus, or enter 2 to test a manually entered word (q to quit): ')
  if userChoice == '1':
    userK = raw_input('Enter a value for k (default is 10): ')
    userN = raw_input('Enter a value for n (default is 2): ')
    if userK.isdigit() and userN.isdigit():
      print('Running %s-fold cross validation of %s-gram model...' % (userK,userN))
      result = kFoldCrossValidation(dataset,train,testSet,int(userK),int(userN))
      print('Success rate of %f' % result)
    elif userK.isdigit():
      print('Running %s-fold cross validation of 2-gram model...' % userK)
      result = kFoldCrossValidation(dataset,train,testSet,int(userK),2)
      print('Success rate of %f' % result)
    elif userN.isdigit():
      print('Running 10-fold cross validation of %s-gram model...' % userN)
      result = kFoldCrossValidation(dataset,train,testSet,10,int(userN))
      print('Success rate of %f' % result)
    else:
      print('Running 10-fold cross validation of 2-gram model...')
      result = kFoldCrossValidation(dataset,train,testSet,10,2)
      print('Success rate of %f' % result)
  
  elif userChoice == '2':
    userK = raw_input('Enter a value for k (default is 10): ')
    userN = raw_input('Enter a value for n (default is 2): ')
    if userK.isdigit() and userN.isdigit():
      print('Running %s-fold cross validation of %s-gram model...' % (userK,userN))
      result = kFoldCrossValidation(dataset,train,testSetWithNoise,int(userK),int(userN))
      print('Success rate of %f' % result)
    elif userK.isdigit():
      print('Running %s-fold cross validation of 2-gram model...' % userK)
      result = kFoldCrossValidation(dataset,train,testSetWithNoise,int(userK),2)
      print('Success rate of %f' % result)
    elif userN.isdigit():
      print('Running 10-fold cross validation of %s-gram model...' % userN)
      result = kFoldCrossValidation(dataset,train,testSetWithNoise,10,int(userN))
      print('Success rate of %f' % result)
    else:
      print('Running 10-fold cross validation of 2-gram model...')
      result = kFoldCrossValidation(dataset,train,testSetWithNoise,10,2)
      print('Success rate of %f' % result)
  
  elif userChoice == '3':
    manualTest(dataset)
  
  else:
    print('Bye!')

if __name__ == '__main__':
    main()
