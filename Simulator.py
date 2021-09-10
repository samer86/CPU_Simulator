# Author Samer Salem CS2
import time
import pandas as pd


class process(object):
    # How many instruction process in holds, it will be edited once the
    # process class initialized
    instructionCount = 1

    arrivalTime = 1
    id = 0
    # place holder to see how much process is left!
    finishedInstuctionCount = 0

    status = 'inTheWay'
    inqueue = False
    waitInQueue = 0
    priority = 0
    # this counter will add up and I only use it for Round Robin so choosing
    # the right process can't be wrong
    executionTime = 0

    # Initilazing process:
    def __init__(self, id, arrivalTime, instructionCount, priority=0):
        self.id = id
        self.arrivalTime = arrivalTime
        self.instructionCount = instructionCount
        self.priority = priority


# Read data from excel sheet and save them in list of lists each list present a process detail ( id, arrivalTime,instructioncount and priority.
data = pd.read_excel('cpu-scheduling.xlsx')

# make process object for each process from the list of process details.

processDetailsList = [elem for index, elem in data.iterrows()]
processList = []
for i in processDetailsList:
    processList.append(process(int(i[0]), int(i[1]), int(i[2]), int(i[3])))


def runProcess(ps):
    '''CPU (like) function this will mimic how processor work'''
    '''each time this process is activated it will add one to finished instruction count and add one to excution time
        When finishinstruction is equal to initial prcess count that means the process is done and it will edit the attribute status
        The return is text string with the function name nad how many instructions left.'''
    result = ''
    ps.finishedInstuctionCount += 1
    ps.executionTime += 1
    processLeft = ps.instructionCount - ps.finishedInstuctionCount
    if processLeft > 0:
        result = f"PID {ps.id} excutes. {processLeft} instruction left."
    if processLeft == 0:
        result = f"PID {ps.id} excutes last instruction."
        ps.status = 'Done'
    return result


class cpuController(object):
    timeUnit = 1
    # list contains all the processes that has not (arrived yet)
    ProcessesInTheWay = []
    # List contains all the (ready or arrived processes)
    queue = []
    # list for the proccess when the cpu is done( sorted by the status "done"
    # for each process)
    doneProcesses = []
    # contains the process that is actually running to memic the cpu as it has its own place.
    # it will have one process at all times or none but I choose list to be as
    # close to the consept of cpu as I could
    runningProcess = []
    # Timer for the Round Robin
    quantum = 3
    # I use this one so I can use it as switch to change the output when the
    # method RR is choosen.
    isThisRR = False

    def __init__(self, processList):
        # when the controller initialized this will be the first place for all
        # the processes
        self.ProcessesInTheWay = processList
        # Place holder to tell the number of the process that we start with
        self.initialPS = processList
        # sorting process by arrivalTime as a start
        self.ProcessesInTheWay = sorted(
            self.ProcessesInTheWay, key=lambda p: p.arrivalTime)
        while len(self.doneProcesses) != len(self.initialPS):
            self.sendProcessToQueue()
            self.processStatusPrinter()
            # I set the timer for 0.25 so the output would be faster.
            time.sleep(0.25)
            self.timeUnit += 1

    def sendProcessToQueue(self):
        '''This precedure take process from inTheWay list to Queue list when the time maches the process arrival time.'''
        for index, i in enumerate(self.queue):
            if i.status == 'Done':
                self.queue.append(self.queue.pop(index))
        for index, i in enumerate(self.ProcessesInTheWay):
            if self.timeUnit == i.arrivalTime:
                i.status = 'onQueue'
                self.queue.append(i)

        self.ProcessesInTheWay = [
            elem for elem in self.ProcessesInTheWay if elem.arrivalTime != self.timeUnit]
        # print(self.ProcessesInTheWay)

    def runProcess(self, ps):
        '''CPU (like) function this will mimic how processor work'''
        '''each time this process is activated it will add one to finished instruction count and add one to excution time
            When finishinstruction is equal to initial prcess count that means the process is done and it will edit the attribute status
            The return is text string with the function name nad how many instructions left.'''
        result = ''
        ps.finishedInstuctionCount += 1
        ps.executionTime += 1
        processLeft = ps.instructionCount - ps.finishedInstuctionCount
        if processLeft > 0:
            result = f"PID {ps.id} Excutes. {processLeft} instruction left."
        if processLeft == 0:
            result = f"PID {ps.id} Excutes last instruction."
            ps.status = 'Done'
            self.doneProcesses.append(self.runningProcess.pop(0))

        return result

    def fifo(self):
        '''First process in Queue get first into the CPU (runProcess precedure)'''

        # If running process has already a process so it will just give it back to cpu
        # If the running process list is empty it will take the first item in
        # the queue list
        if len(self.runningProcess) > 0:
            return self.runningProcess[0]
        else:
            return self.queue[0]

    def sjf(self):
        '''Shortest Jobb First '''
        # if running process list has process already then just send it back to
        # the cpu
        if len(self.runningProcess) > 0:
            return self.runningProcess[0]
        else:
            # selecet the minst instruction cound from the process that has the
            # lowest instruction count
            lowestInstructionCount = min(
                self.queue, key=lambda p: p.instructionCount).instructionCount
            # get a list with all the process that has the minst instruction
            # number in the queue.
            proessWithLowestInstructionCount = list(
                filter(lambda x: x.instructionCount == lowestInstructionCount, self.queue))
            # sort the list that contains the lowest instruction count number by arrival time so the first
            # This insure that if there were more than one process with the same (lowest instruction count number )
            # then the first one to arrive will be the first to select.
            proessWithLowestInstructionCount = sorted(
                proessWithLowestInstructionCount, key=lambda p: p.arrivalTime)
            # return seletect process from the queue
            return proessWithLowestInstructionCount[0]

    def priority(self):
        '''Processes with the lowest priority number will get selected first'''
        # if running process has allready a process so selected it again
        if len(self.runningProcess) > 0:
            return self.runningProcess[0]
        else:
            # get the lowest priority value from a process that has that value.
            lowestPriorityValue = min(
                self.queue, key=lambda p: p.priority).priority
            # Using list generator to select all the processes with the lowest
            # priority value from the queue
            lowestPriorityList = [
                elem for elem in self.queue if elem.priority == lowestPriorityValue]
            # sort the list by arrival time incase there are more than one
            # process with the same priority so it will fall back to FIFO
            # method
            lowestPriorityList = sorted(
                lowestPriorityList, key=lambda p: p.arrivalTime)
            # return the first item in the list
            return lowestPriorityList[0]

    def RR(self):
        '''Rround Robin my worse headaches'''
        # Changin this attribute will change the way the output precedure
        # operate
        self.isThisRR = True
        # If the there are a process in the runningProcess list and the quantum
        # over zero then select the same process and substract the quantum
        if len(self.runningProcess) > 0 and self.quantum >= 0:
            self.quantum -= 1
            return self.runningProcess[0]
        # If the process is not done yet but the quanum time is up then reset
        # the quantum timer and return the running process to queue.
        elif len(self.runningProcess) > 0 and self.quantum <= 0:
            self.quantum = 3
            if self.runningProcess[0].status != 'Done':
                self.queue.append(self.runningProcess.pop(0))
            else:
                self.doneProcesses.append(self.runningProcess.pop(0))
            # Returning none means no running process and the cpu is in context
            # switch state.
            return None
        # If there are no running process in the running process list and the
        # quantum timer is max then:
        elif len(self.runningProcess) == 0 and self.quantum == 3:
            # Get the mins execution time from all process in the queue at the moment.
            # using the .exectutionTime so it chose the value of attribute
            # (executionTime) only and not the whole process.
            LowestExecutionTime = min(
                self.queue, key=lambda x: x.executionTime).executionTime
            # Select all the process with the lowest exectution time in one list.
            # This can be done via generator but for learning purpose I use
            # list(filter.... to try new things.
            processWithLowestExecutionTime_List = list(
                filter(lambda p: p.executionTime == LowestExecutionTime, self.queue))
            # Finally sort the list that contains the process by the
            # instructionCount so it will fall back to SJF if there are more
            # than one process to select from
            processWithLowestExecutionTime_List = sorted(
                processWithLowestExecutionTime_List, key=lambda p: p.instructionCount)
            self.quantum -= 1
            # Return the selected process after substract the quantum timer.
            return processWithLowestExecutionTime_List[0]
        else:
            # Incase the process ended before the timer so this will reset the
            # quantum timer and set the cpu in context state.
            self.quantum = 3
            return None

    def processStatusPrinter(self):
        '''This precedure  generate the output for the queue list and running processes'''
        # First step in this procedure is to check if there is something in the runningProcess AND the queue
        # IF not that means the cpu is idle and the queue is empty.
        if len(self.runningProcess) > 0 or len(self.queue) > 0:
            # Selected process to send to cpu
            # this can be changed according to the desired algorithm
            # options:
            # selectedPS = self.fifo()
            # selectedPS = self.sjf()
            # selectedPS = self.priority()
            selectedPS = self.RR()

            # moving selected process from queue to running if its not there.
            # It can be done with IF statement, but I use try /except for
            # learning purpose.
            try:
                self.queue.remove(selectedPS)
                self.runningProcess.append(selectedPS)
            except BaseException:
                pass

            # Gather statement and waiting time to all process on queue that
            # are waiting
            queueText = ''
            # If queue has items (processes) then loop through
            if len(self.queue) > 0:
                for i in self.queue:
                    i.status = 'inQueue'
                    # Adding one to waiting time attribute to all processes on the queue.
                    # This make it easy to regester and keep track for waiting
                    # time for each process
                    i.waitInQueue += 1
                    # adding str to the queue statement contains the process id
                    # and its waiting time so far.
                    queueText += f"PID {i.id} wait={i.waitInQueue}TU. "
            else:
                # If there are no processes in the queue so the text will be
                # just no queue.
                queueText = ' No queue.'

            # I use selectedPS as switch to decide what to print each time the time passes:
            # None case it means there are no selectedprocess and the cpu in
            # context state when the the choosen logarithm is Round Robin
            if selectedPS is None:
                print(
                    f'Time Unit {self.timeUnit} Context switch.')
                print(
                    f"{queueText}")
            # Withen the RR procedure I change the value of self.isThisRR to
            # True so it will print RR standard ( required data)
            elif self.isThisRR:
                # F strings contains the time unit , return the runProcess
                # function ( CPU ), quantum timer when the cpu is not in
                # context switch state
                print(
                    f"Time Unit {self.timeUnit}: {self.runProcess(selectedPS)} Q={self.quantum +1} \n{queueText} \n")
            else:
                # Last if none of the above accords then the selected algorithm
                # is not RR and can be printed with the following syntax
                print(
                    f"Time Unit {self.timeUnit}: {self.runProcess(selectedPS)}\n {queueText}\n")

        else:
            # IF the queue list and runingProcess list are empty
            # but not the inTheWayprocess list then the cpu is idle
            print(f'Time Unit {self.timeUnit}: Cpu is idle')


if __name__ == "__main__":
    start = cpuController(processList)
