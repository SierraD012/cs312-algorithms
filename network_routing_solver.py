#!/usr/bin/python3


from CS312Graph import *
import time


class NetworkRoutingSolver:
    def __init__( self, display ):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    # This one just picks out the shortest past from src->dest within your MST
    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        path_edges = []
        total_length = 0

        print("=======================")
        print(">>NRS: getSP(): nodes size="+str(len(self.network.nodes)))
        currNode = self.network.nodes[destIndex] #start from the destination node and work backwards
        print(">>NRS: getSP(): starting on node= " + str(currNode))
        #edges_left = 3 #this is just set to 3 for the dummy version

        # Check if there really was a path found - if not, it's probably unreachable
        if currNode.incomingEdge is None:
            print(">>NRS: getSP(): done, no path found!!")
            return {'cost': float('inf'), 'path': path_edges}

        # Add up the MST edges starting from final node and going back to start node
        while currNode.incomingEdge is not None:
            currEdge = currNode.incomingEdge
            path_edges.append( (currEdge.src.loc, currEdge.dest.loc,'{:.0f}'.format(currEdge.length)) )
            total_length += currEdge.length
            currNode = currEdge.src # back up to the previous node

        print(">>NRS: getSP(): done, #path_edges="+str(len(path_edges)))
        return {'cost':total_length, 'path':path_edges}

    # If "use both" was checked in the GUI, then this fn will be called 2x,
    # once with use_heap = True and once with use_heap = False
    # This one runs all of Dijkstra's and creates an MST
    def computeShortestPaths( self, srcIndex, use_heap ):
        print("=======================")
        print(">>NRS: computeSP(): starting, useHeap="+str(use_heap))

        self.source = srcIndex
        startNode = self.network.nodes[srcIndex]
        startNode.distance = 0; #init the first node

        t1 = time.time()

        if not use_heap:   # USE UNSORTED ARRAY
            priorityQueue = self.makeQueue()

            while len(priorityQueue) > 0:
                #get first node out of queue
                min = self.getMinNode(priorityQueue, None, use_heap) #unsortedArr doesn't use the dictionary
                priorityQueue.remove(min)

                # get min's neighbors and organize them by length
                for edge in min.neighbors:
                    if (min.distance + edge.length) < edge.dest.distance:  #save new dist as the smallest dist
                        edge.dest.incomingEdge = edge #link destNode to its previous edge so we can do getShortestPath()
                        edge.dest.distance = min.distance + edge.length #update the destNode's new shortest dist

        else:  # USE MINHEAP
            priorityQueue = [startNode, startNode] #doing this twice so there will always be a 0 on top to make dist compares easy
            nodeToIndexDict = {}


            while len(priorityQueue) > 1:  # while there are still nodes in the pQueue (minHeap will always have 1 head node)
                # get first node out of queue
                min = self.getMinNode(priorityQueue, nodeToIndexDict, use_heap)

                # get min's neighbors and organize them by length
                for edge in min.neighbors:
                    if (min.distance + edge.length) < edge.dest.distance:  # if the dist from currNode -> destNode, save new dist as the smallest dist
                        edge.dest.incomingEdge = edge
                        edge.dest.distance = min.distance + edge.length  # update the destNode's new shortest dist
                        #Check if the destNode is not already in the dictionary
                        heapIndex = 0
                        if edge.dest.node_id not in nodeToIndexDict:
                            # if node doesn't exist in dictionary already, add it to heap AND dictionary
                            heapIndex = len(priorityQueue)
                            nodeToIndexDict[edge.dest.node_id] = heapIndex
                            priorityQueue.append(edge.dest)
                        else: #the node is already in the dictionary
                            heapIndex = nodeToIndexDict.get(edge.dest.node_id)
                        # Resort the pQueue so smallest is at top
                        self.bubbleUp(priorityQueue, nodeToIndexDict, heapIndex)

        t2 = time.time()
        return (t2-t1)


    # initializes the pQueue by setting each node's value to infinity and setting the start node's distance to 0
    def makeQueue(self):
        #priorityQueue = list() #this can be a regular array or a min heap
        priorityQueue = list(self.network.nodes)
        priorityQueue[self.source].distance = 0 # this is the equivalent of setting node A's dist column to 0

        return priorityQueue

    #searches through the pQueue and finds the node with the minimum length, returns its index
    def getMinNode(self, pQueue, dict, use_heap):

        if use_heap:
            #this branch gets the min node AND deletes it from the pQueue
            #Checking right here if the left child is smaller than right child - picks the min from those
            minHeapID = 1
            if len(pQueue) >= 3: #it'll only have 2 children to choose from if it has 3+ nodes
                if pQueue[1].distance < pQueue[2].distance:
                    minHeapID = 1
                else:
                    minHeapID = 2

            min = pQueue[minHeapID]  # we're not doing 0 because we're keeping a permanent "0" head on this minheap
            pQueue[minHeapID] = pQueue[len(pQueue)-1]
            pQueue.pop()  # take off the top node since it's the smallest
            self.bubbleDown(pQueue, dict, minHeapID)
            return min

        else:
            # it's the array, so just return the index of the node that has the shortest distance
            #this is going to have to be O(|v|) pretty much no matter what
            minNode = pQueue[0]
            for node in pQueue:
                if node.distance < minNode.distance:
                    minNode = node

            return minNode


    # Resorts the minheap so that the node with shortest distance is on top - also adds to the dictionary
    def bubbleUp(self, pQueue, dict, heapIndex):
        i = heapIndex  # start bubbling up from the heapIndex passed in
        while (i // 2) > 0:
          if pQueue[i].distance < pQueue[i // 2].distance:     #if child is less distance than parent
             parent = pQueue[i // 2]
             pQueue[i // 2] = pQueue[i]
             pQueue[i] = parent
             #Update the parent/child's heap indices to mirror the swap
             dict[pQueue[i].node_id] = i
             dict[pQueue[i // 2].node_id] = i // 2
          i = i // 2

    # Resorts the minheap so that the min node (which is either the first left or first right child) moves down to the bottom
    def bubbleDown(self, pQueue, dict, heapIndex):
        i = heapIndex
        while (i * 2) <= (len(pQueue)-1):
            mci = self.pickMinChildIndex(pQueue, i)
            if pQueue[i].distance > pQueue[mci].distance:
                parent = pQueue[i]
                pQueue[i] = pQueue[mci]
                pQueue[mci] = parent

                # Update the parent/child's heap indices to mirror the swap
                dict[pQueue[i].node_id] = i
                dict[pQueue[mci].node_id] = mci
            i = mci


    # Given a node's heap index, returns the INDEX of the child that has the smaller distance value
    def pickMinChildIndex(self, pQueue, i):
        if (i * 2 + 1) > (len(pQueue)-1):
            return i * 2
        else:
            if pQueue[i * 2].distance < pQueue[i * 2 + 1].distance:
                return i * 2
            else:
                return i * 2 + 1
