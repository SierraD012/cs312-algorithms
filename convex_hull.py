#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
#elif PYQT_VER == 'PYQT4':
#    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

class ConvexHullSolver:
    def __init__( self, display ):
        self.points = None
        self.gui_display = display

    # Main function called by the GUI - generates points, sorts them, and calls the makeConvex solver
    def compute_hull( self, unsorted_points ):
        assert( type(unsorted_points) == list and type(unsorted_points[0]) == QPointF )

        n = len(unsorted_points)
        print( '>>Computing Hull for set of {} points'.format(n) )

        t1 = time.time()
        sorted_points = sorted(unsorted_points, key=lambda pt: pt.x())
        t2 = time.time()
        print('Time Elapsed (Sorting): {:3.8f} sec'.format(t2-t1))

        t3 = time.time()
        convexHullPoints = self.makeConvex(sorted_points)
        t4 = time.time()

        # Create QLineFs from the convex hull points and send them all to the GUI
        convexHullLines = []
        for i in range(len(convexHullPoints)):
            convexHullLines.append(QLineF(convexHullPoints[i], convexHullPoints[(i + 1) % len(convexHullPoints)]))

        self.gui_display.addLines(convexHullLines, (0, 0, 255))

        print('Time Elapsed (Convex Hull): {:3.8f} sec'.format(t4-t3))
        self.gui_display.displayStatusText('Time Elapsed (Convex Hull): {:3.8f} sec'.format(t4-t3))
        self.gui_display.update()


    # Recursively splits the given pointsList in half, and sorts it in CW order when the list is <= 3 points long
    def makeConvex( self, pointsList ):
       # print(">>MAKECONVEX(): starting")

        # BASE CASE - 2 or 3 points
        if len(pointsList) <= 3 :
            # an array of 2 points will always be sorted CW, but an array of 3 points won't necessarily be sorted
            if len(pointsList) == 3:
                slope1 = self.findSlope(pointsList[0], pointsList[1])
                slope2 = self.findSlope(pointsList[0], pointsList[2])
                if slope2 > slope1:
                    # swap points at pos 1 and pos 2
                    temp = pointsList[2]
                    pointsList[2] = pointsList[1]
                    pointsList[1] = temp
                elif pointsList[1].y() == pointsList[2].y():
                    if pointsList[0].y() > pointsList[1].y():
                        # swap points at pos 1 and pos 2
                        temp = pointsList[2]
                        pointsList[2] = pointsList[1]
                        pointsList[1] = temp
            return pointsList

        # Split the points in half
        half = len(pointsList) // 2
        leftSidePoints = pointsList[:half] # from 0 to half
        rightSidePoints = pointsList[half:] # If n is odd, rightSide will be 1 larger than leftSide

        # Recurse until the list is 2 or 3 elements long (base cases)
        leftHull = self.makeConvex(leftSidePoints)
        rightHull = self.makeConvex(rightSidePoints)

        # Merge leftHull and rightHull
        mergedHull = self.mergeHulls(leftHull, rightHull)

        return mergedHull


    # Given two hull arrays of QPointFs, merges the two hulls into one shape and returns the merged array
    def mergeHulls(self, leftHull, rightHull):

        leftHullPivot_Index = self.findRightmostPoint(leftHull)
        rightHullPivot_Index = 0

        leftHull_upperTan_index, rightHull_upperTan_index = self.findTangentPoints(leftHull, rightHull,leftHullPivot_Index, rightHullPivot_Index)
        rightHull_lowerTan_index, leftHull_lowerTan_index = self.findTangentPoints(rightHull, leftHull, rightHullPivot_Index, leftHullPivot_Index)

        leftHull_upperTan_index = leftHull_upperTan_index % len(leftHull)
        leftHull_lowerTan_index = leftHull_lowerTan_index #% len(leftHull)
        rightHull_upperTan_index = rightHull_upperTan_index % len(rightHull)
        rightHull_lowerTan_index = rightHull_lowerTan_index % len(rightHull)

        # Merge the two arrays in clockwise order
        mergedHull = leftHull[0:leftHull_upperTan_index+1]
        mergedHull += (rightHull[rightHull_upperTan_index:rightHull_lowerTan_index+1])
        # Special cases for when the index is 0
        if rightHull_lowerTan_index == 0:
            mergedHull += rightHull[rightHull_upperTan_index:]
            mergedHull.append(rightHull[0])

        if not leftHull_lowerTan_index == 0:
            mergedHull += (leftHull[leftHull_lowerTan_index:])

        return mergedHull

    # Finds the upper and lower tangent points for a given left/right hull,
    # depending on what order the hulls/pivot_Indices are passed in
    def findTangentPoints(self, leftHull, rightHull, leftHullPivot_Index, rightHullPivot_Index):

        currSlope = self.findSlope(leftHull[leftHullPivot_Index], rightHull[rightHullPivot_Index])
        updateNeeded = True

        while updateNeeded:
            updateNeeded = False

            left_slope_decreasing = True
            while left_slope_decreasing:
                potentialLeftHullPivot_index = leftHullPivot_Index - 1
                if potentialLeftHullPivot_index < 0:
                    potentialLeftHullPivot_index = len(leftHull) - 1

                nextSlope = self.findSlope(leftHull[potentialLeftHullPivot_index], rightHull[rightHullPivot_Index])

                if nextSlope > currSlope:
                    left_slope_decreasing = False
                else:
                    updateNeeded = True
                    leftHullPivot_Index = potentialLeftHullPivot_index
                    currSlope = nextSlope

            right_slope_increasing = True
            while right_slope_increasing:
                potentialRightHullPivot_index = rightHullPivot_Index + 1
                if potentialRightHullPivot_index == len(rightHull):
                    potentialRightHullPivot_index = 0

                nextSlope = self.findSlope(leftHull[leftHullPivot_Index], rightHull[potentialRightHullPivot_index])

                if nextSlope < currSlope:
                    right_slope_increasing = False
                else:
                    updateNeeded = True
                    rightHullPivot_Index = potentialRightHullPivot_index
                    currSlope = nextSlope

        return leftHullPivot_Index, rightHullPivot_Index


    # Given the leftHull array of points, iterates until it finds the one with the highest x-value
    def findRightmostPoint(self, leftHull):
        assert( type(leftHull) == list and type(leftHull[0]) == QPointF )

        for i in range(len(leftHull)):
            if (i+1) >= len(leftHull):
                # we can assume the current point is the rightmost
                return i

            if leftHull[i+1].x() < leftHull[i].x():
                # the points are no longer increasing on the x-axis, so take the current point as the rightmost one
                return i

    # Given two QPointFs, returns the slope between them
    def findSlope(self, point1, point2):
        assert (type(point1) == QPointF and type(point2) == QPointF)

        rise = point2.y() - point1.y()
        run = point2.x() - point1.x()
        return rise / run