import math
import random
import numpy
BUSY=1
IDLE=0
ARRIVAL=1
DEPARTURE=2
CONSTANT=1
UNIFORM=2
EXPONENTIAL=3

table=[]
aux=[]

class Request:
    def __init__(self,requestId,serviceTime,waitingTime,responseTime,isTimedOut,coreId,threadId,thinkTime,arrivalTime):
        self.requestId=requestId
        self.serviceTime=serviceTime
        self.waitingTime=waitingTime
        self.responseTime=responseTime
        self.isTimedOut=isTimedOut
        self.coreId=coreId
        self.threadId=threadId
        self.thinkTime=thinkTime
        self.arrivalTime=arrivalTime
    def __str__(self):
        return str(self.requestId)+" "+str(self.serviceTime)+" "+str(self.waitingTime)+" "+str(self.responseTime)+" "+str(self.isTimedOut)+" "+str(self.coreId)+" "+str(self.threadId)+" "+str(self.thinkTime)
    def setRequestId(self,requestId):
        self.requestId=requestId
    def getRequestId(self):
        return self.requestId
    def setServiceTime(self,serviceTime):
        self.serviceTime=serviceTime
    def getServiceTime(self):
        return self.serviceTime
    def setWaitingTime(self,waitingTime):
        self.waitingTime=waitingTime
    def getWaitingTime(self):
        return self.waitingTime
    def setResponseTime(self,responseTime):
        self.responseTime=responseTime
    def getResponseTime(self):
        return self.responseTime
    def setIsTimedOut(self,isTimedOut):
        self.isTimedOut=isTimedOut
    def getIsTimedOut(self):
        return self.isTimedOut
    def setCoreId(self,coreId):
        self.coreId=coreId
    def getCoreId(self):
        return self.coreId
    def setThreadId(self,threadId):
        self.threadId=threadId
    def getThreadId(self):
        return self.threadId
    def setThinkTime(self,thinkTime):
        self.thinkTime=thinkTime
    def getThinkTime(self):
        return self.thinkTime
    def setArrivalTime(self,arrivalTime):
        self.arrivalTime=arrivalTime
    def getArrivalTime(self):
        return self.arrivalTime


class Server:
    def __init__(self,status,simulationTime,numberInQueue,timeoutTime,numberOfCores,numberOfThreads,maxQueueLength,serviceTimeDistribution):
        self.status=status
        self.simulationTime=simulationTime
        self.numberInQueue=numberInQueue
        self.timeoutTime=timeoutTime
        self.numberOfCores=numberOfCores
        self.numberOfThreads=numberOfThreads
        self.maxQueueLength=maxQueueLength
        self.serviceTimeDistribution=serviceTimeDistribution
        #buffer to store the requests to be serviced
        self.queue=[]
        #data structure to store the events - Arrival and Departure
        self.priorityQueue=[]
        #data structure to store the dropped requests
        self.droppedRequests=[]
        #Stores threads
        self.threadPool=[]
        #keeps track of requests which result in good put
        self.goodputRequests=0
        #keeps track of requests which result in bad put
        self.badputRequests=0
        #Total response time
        self.totalResponseTime=0.0

        self.usedThreadSet=set()

        self.intermediateResponseTimes=[]

    def initialize(self):
        #initializing the thread pool
        self.threadPool=[self.numberOfThreads for i in range(self.numberOfCores)]
        self.status=IDLE
        self.simulationTime=0.0
        self.timeLastEvent=0.0
        self.queue=[]
        self.priorityQueue=[]
        self.droppedRequests=[]
        self.goodputRequests=0
        self.badputRequests=0
        self.totalResponseTime=0.0
        self.usedThreadSet=set()
    def setStatus(self,status):
        self.status=status
    def getStatus(self):
        return self.status
    def setSimulationTime(self,simulationTime):
        self.simulationTime=simulationTime
    def getSimulationTime(self):
        return self.simulationTime
    def setNumberInQueue(self,numberInQueue):
        self.numberInQueue=numberInQueue
    def getNumberInQueue(self):
        return self.numberInQueue
    def setTimeoutTime(self,timeoutTime):
        self.timeoutTime=timeoutTime
    def getTimeoutTime(self):
        return self.timeoutTime
    def setNumberOfCores(self,numberOfCores):
        self.numberOfCores=numberOfCores
    def getNumberOfCores(self):
        return self.numberOfCores
    def setNumberOfThreads(self,numberOfThreads):
        self.numberOfThreads=numberOfThreads
    def getNumberOfThreads(self):
        return self.numberOfThreads
    def setMaxQueueLength(self,maxQueueLength):
        self.maxQueueLength=maxQueueLength
    def getMaxQueueLength(self):
        return self.maxQueueLength
    def setGoodputRequests(self,goodputRequest):
        self.goodputRequests=goodputRequest
    def getGoodputRequests(self):
        return self.goodputRequests
    def setBadputRequests(self,badputRequest):
        self.badputRequests=badputRequest
    def getBadputRequests(self):
        return self.badputRequests
    def setServiceTimeDistribution(self,serviceTimeDistribution):
        self.serviceTimeDistribution=serviceTimeDistribution
    def getServiceTimeDistribution(self):
        return self.serviceTimeDistribution
    def setTimeLastEvent(self,timeLastEvent):
        self.timeLastEvent=timeLastEvent
    def getTimeLastEvent(self):
        return self.timeLastEvent
    #returns the core Id and thread Id of free thread. Otherwise false
    def getFreeThread(self):
        i=0
        while i<len(self.threadPool):
            if self.threadPool[i]>0:
                self.threadPool[i]-=1
                return (i,self.threadPool[i])
            i+=1
        return False

class Event:
    def __init__(self,request,eventType,timeStamp):
        self.request=request
        self.eventType=eventType
        self.timeStamp=timeStamp
    def setRequest(self,request):
        self.request=request
    def getRequest(self):
        return self.request
    def setEventType(self,eventType):
        self.eventType=eventType
    def getEventType(self):
        return self.eventType
    def setTimeStamp(self,timeStamp):
        self.timeStamp=timeStamp
    def getTimeStamp(self):
        return self.timeStamp

#creating the global object of server
server=Server(IDLE,0.0,0,0.0,0,0,50,CONSTANT)

def arrive():
    #if buffer is full, then drop the arrival request
    if len(server.queue)>server.getMaxQueueLength():
        droppedEvent=server.priorityQueue.pop(0)
        server.droppedRequests.append(droppedEvent.getRequest())
    else:
        server.setStatus(BUSY)
        #getting the core Id and thread Id of free thread
        freeThread=server.getFreeThread()
        #popping arrival event from priority queue
        request=server.priorityQueue.pop(0).getRequest()
        server.queue.append(request)
        server.setNumberInQueue(server.getNumberInQueue()+1)
        #pushing the request in buffer, because free thread is not available
        if freeThread==False:
            server.setSimulationTime(request.getArrivalTime())
            server.setNumberInQueue(server.getNumberInQueue()+1)
        else:
        #servicing the arrival request
            request=server.queue.pop(0)
            coreAndThreadId=freeThread
            server.usedThreadSet.add(coreAndThreadId)
            request.setCoreId(coreAndThreadId[0])
            request.setThreadId(coreAndThreadId[1])
            server.setSimulationTime(server.getSimulationTime()+request.getArrivalTime())
            #creating departure event for the queue and putting it in priority queue
            departure=Event(request,DEPARTURE,server.getSimulationTime()+request.getServiceTime())
            server.priorityQueue.append(departure)
            server.priorityQueue.sort(key=compareEvent)
        table.append([server.getSimulationTime(),len(server.queue),"ARRIVAL"])

def depart():
    if server.getNumberInQueue()==0:
        server.setStatus(IDLE)
    else:
        event=server.priorityQueue.pop(0)
        request=event.getRequest()
        server.setSimulationTime(event.getTimeStamp())
        server.setNumberInQueue(server.getNumberInQueue()-1)
        request.setResponseTime(server.getSimulationTime()-request.getArrivalTime())
        server.totalResponseTime+=request.getResponseTime()
        request.setWaitingTime(request.getResponseTime()-request.getServiceTime())
        if server.getTimeoutTime()<request.getWaitingTime():
            request.setIsTimedOut(True)
            server.setBadputRequests(server.getBadputRequests()+1)
        else:
            server.setGoodputRequests(server.getGoodputRequests()+1)
        server.threadPool[request.getCoreId()]+=1
        table.append([server.getSimulationTime(),len(server.queue),'DEPARTURE'])
        aux.append(request)
        serviceTimeDistribution=server.getServiceTimeDistribution()
        serviceTime=0.0
        if serviceTimeDistribution==CONSTANT: serviceTime=42.0
        if serviceTimeDistribution==UNIFORM: serviceTime=numpy.random.uniform(25.0,59.0)
        if serviceTimeDistribution==EXPONENTIAL: serviceTime=numpy.random.exponential(42.0)
        request=Request(request.getRequestId(),serviceTime,math.inf,math.inf,False,server.getNumberOfCores(),server.getNumberOfThreads(),1000.0,server.getSimulationTime()+request.getThinkTime())
        event=Event(request,ARRIVAL,server.getSimulationTime()+request.getThinkTime())
        server.priorityQueue.append(event)
        if len(server.queue)>0:
            request=server.queue.pop(0)
            server.setNumberInQueue(server.getNumberInQueue()-1)
            coreAndThreadId=server.getFreeThread()
            request.setCoreId(coreAndThreadId[0])
            request.setThreadId(coreAndThreadId[1])
            departure=Event(request,DEPARTURE,server.getSimulationTime()+request.getServiceTime())
            server.priorityQueue.append(departure)
            server.priorityQueue.sort(key=compareEvent)


def compareEvent(e):
    return e.getTimeStamp()

numberOfRuns=0
numberOfCustomersDelayed=0
numberOfDelaysRequired=0
numberOfRuns=int(input("Enter number of runs : "))
numberOfCores=int(input("Enter number of cores : "))
numberOfThreads=int(input("Enter number of threads : "))
maximumQueueLength=int(input("Enter maximum queue length : "))
timeoutTime=float(input("Enter the value of timeout time : "))
print("Enter service time distribution : ")
print("1. Constant")
print("2. Uniform")
print("3. Exponential")
serviceTimeDistribution=int(input())
numberOfUsers=int(input("Enter number of users : "))
numberOfDelaysRequired=int(input("Enter number of delays required : "))

server.setNumberOfCores(numberOfCores)
server.setNumberOfThreads(numberOfThreads)
server.setMaxQueueLength(maximumQueueLength)
server.setTimeoutTime(timeoutTime)
server.setServiceTimeDistribution(serviceTimeDistribution)

totalDroppedRequests=0
totalDropRate=0.0
totalSimulationTime=0.0
totalGoodputRequests=0
totalBadputRequests=0
totalGoodput=0.0
totalBadput=0.0
totalThroughput=0.0
totalResponseTime=0.0
totalUtilization=0.0

k=0
while k<numberOfRuns:
    server.initialize()
    numberOfCustomersDelayed=0

    serviceTimeDistribution=server.getServiceTimeDistribution()
    serviceTime=0.0
    i=0
    while i<numberOfUsers:
        if serviceTimeDistribution==CONSTANT: serviceTime=42.0
        if serviceTimeDistribution==UNIFORM: serviceTime=numpy.random.uniform(25.0,59.0)
        if serviceTimeDistribution==EXPONENTIAL: serviceTime=numpy.random.exponential(42.0)
        request=Request(i,serviceTime,math.inf,math.inf,False,server.getNumberOfCores(),server.getNumberOfThreads(),1000.0,0.0)
        event=Event(request,ARRIVAL,request.getThinkTime())
        server.priorityQueue.append(event)
        i+=1
    server.priorityQueue.sort(key=compareEvent)
    while numberOfCustomersDelayed<numberOfDelaysRequired and len(server.priorityQueue)>0:
        if server.priorityQueue[0].getEventType()==ARRIVAL:
            arrive()
        else:
            depart()
        numberOfCustomersDelayed+=1
    totalDroppedRequests+=len(server.droppedRequests)
    totalDropRate+=(len(server.droppedRequests)/(server.getGoodputRequests()+server.getBadputRequests()))
    totalSimulationTime+=server.getSimulationTime()
    totalGoodputRequests+=server.getGoodputRequests()
    totalGoodput+=(server.getGoodputRequests()/server.getSimulationTime())
    totalBadputRequests+=server.getBadputRequests()
    totalBadput+=(server.getBadputRequests()/server.getSimulationTime())
    totalThroughput+=((server.getGoodputRequests()+server.getBadputRequests())/server.getSimulationTime())
    totalResponseTime+=(server.totalResponseTime/(server.getGoodputRequests()+server.getBadputRequests()))
    totalUtilization+=(len(server.usedThreadSet)/(server.getNumberOfThreads()*server.getNumberOfCores()))
    server.intermediateResponseTimes.append((server.totalResponseTime)/(server.getGoodputRequests()+server.getBadputRequests()))
    k+=1

print("Simulation Time is : ",totalSimulationTime/numberOfRuns)
print("Good Put is : ",totalGoodputRequests,totalGoodput/numberOfRuns)
print("Bad Put is : ",totalBadputRequests,totalBadput/numberOfRuns)
print("Throughput is : ",totalThroughput/numberOfRuns)
print("Number of drops : ",totalDroppedRequests)
print("Request Drop Rate : ",totalDropRate)
print("Total Response Time : ",totalResponseTime)
print("Server Utilization : ",totalUtilization/numberOfRuns)
#print(server.intermediateResponseTimes)
averageResponseTime=totalResponseTime/numberOfRuns
variance=0.0
for k in server.intermediateResponseTimes:
    variance+=((averageResponseTime-k)**2)
variance=variance/numberOfRuns
print("Average Response Time : ",averageResponseTime)
print("Variance : ",variance)
confidenceIntervalLow=averageResponseTime-1.96*(math.sqrt(variance/numberOfRuns))
confidenceIntervalHigh=averageResponseTime+1.96*(math.sqrt(variance/numberOfRuns))
print("Confidence Interval is : "+str(confidenceIntervalLow)+" to "+str(confidenceIntervalHigh))