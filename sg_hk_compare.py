# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:40:46 2017

@author: cfd
"""
'''
函数功能：通过集合，将收集到的内容整理成集合的形式
'''
def createVocabList(dataSet):
    vocabSet = set()     #创建一个空集
    for document in dataSet: 
        vocabSet = vocabSet | set(document) #创建两个集合的并集
    return list(vocabSet)

'''
函数功能：统计出出现频率最高的前30个单词
'''
def calcMostFreq(vocabList, fullText):
    import operator
    freqDict = {}
    for token in vocabList:
        freqDict[token] = fullText.count(token)

    sortedFreq = sorted(freqDict.items(), key = operator.itemgetter(1), reverse = True)
    return sortedFreq[:30]

'''
函数功能：采用词袋模型，将每一则rss信息转换成词向量
'''
def bagOfWord2VecMN(vocabList, inputSet):
    returnVec = [0]*len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
    return returnVec
'''
函数功能：朴素贝叶斯分类器训练函数
'''
def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix) #矩阵的长度
    numWords =  len(trainMatrix[0]) #矩阵的列长度
    pAbusive =  sum(trainCategory) / float(numTrainDocs) #计算属于侮辱性文档的概率
    p0Num = ones(numWords)
    p1Num = ones(numWords)
    p0Denom = 2.0
    p1Denom = 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = log(p1Num / p1Denom)
    p0Vect = log(p0Num / p0Denom)
    return p0Vect, p1Vect, pAbusive    

'''
函数功能：朴素贝叶斯分类函数
'''    
def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    p1 = sum(vec2Classify * p1Vec) + log(pClass1) #只需要对vec2Classify所对应的词概率进行求和
    p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)                                                 
    if p1 > p0:
        return 1
    else:
        return 0
'''
函数功能：具体处理收到rss信息,并且计算出概率
'''
def localWords(feed1, feed0):
    import feedparser
    docList = []
    classList = [] 
    fullText = []
    minLen = min(len(feed1['entries']), len(feed0['entries']))
    for i in range(minLen):
        wordList = textParse(feed1['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(feed0['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = createVocabList(docList) #生成字典列表
    top30Words = calcMostFreq(vocabList, fullText) #选取出 出现频率最高的30个词
    for pairW in top30Words: #去掉30个出现频率最高的单词
        if pairW[0] in vocabList:
            vocabList.remove(pairW[0])
    trainingSet = list(range(2*minLen))
    testSet = []
    for i in range(20): #选取数据集中的20个数据作为测试数据
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del(trainingSet[randIndex])
    trainMat = []
    trainClasses = []
    for docIndex in trainingSet:
        trainMat.append(bagOfWord2VecMN(vocabList, docList[docIndex]))#采用词袋模型，将每一则rss数据转化为词向量
        trainClasses.append(classList[docIndex])
    p0V, p1V, pSpam = trainNB0(array(trainMat), array(trainClasses)) #计算出条件概率
    errorCount = 0.0
    for docIndex in testSet: #测试数据来测试训练结果
        wordVector = bagOfWord2VecMN(vocabList, docList[docIndex]) #转换成词向量
        if classifyNB(array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
            errorCount += 1
    print('the error rate is: ', float(errorCount) / len(testSet))
    return vocabList, p0V, p1V


'''
函数功能：处理收到rss信息，统计出现频率较高的词
'''
def getTopWords(sg, hk):
    import operator
    vocabList, p0V, p1V = localWords(sg, hk)
    topSG = []
    topHK = []
    for i in range(len(p0V)):
        if p0V[i] > -4.5: #大于3.125%的词
            topSG.append((vocabList[i], p0V[i]))
        if p1V[i] > -4.5:
            topHK.append((vocabList[i], p1V[i]))
    sortedSG = sorted(topSG, key=lambda pair: pair[1], reverse=True) #按照列表中元组里的第二个元素进行排序
    print('SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**')
    for item in sortedSG:
        print(item[0])
    sortedHK = sorted(topHK, key=lambda pair: pair[1], reverse=True)
    print('NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**')
    for item in sortedHK:
        print(item[0])

'''
函数功能：通过feedparse(rss阅读器)读取craigslist中新加坡和香港的广告信息
'''
def getRSS():
    sg = feedparser.parse('http://singapore.craigslist.com.sg/search/stp?format=rss')
    hk = feedparser.parse('http://hongkong.craigslist.hk/search/stp?format=rss')
    getTopWords(sg, hk)


getRSS()