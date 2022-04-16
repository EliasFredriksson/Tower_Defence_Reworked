class PointerElement:
    def __init__(self):
        self.item = None
        self.nextItem = PointerElement
        self.prevItem = PointerElement

        self.hasItem = False
        self.hasNext = False
        self.hasPrev = False
        
    def setNext(self, nextItem):
        if nextItem == False:
            self.nextItem = PointerElement
            self.hasNext = False
        else:
            self.nextItem = nextItem
            self.nextItem.setPrev(self)
            self.hasNext = True

    def setItem(self, item):
        self.item = item
        self.hasItem = True
    
    def setPrev(self, prevItem):
        self.prevItem = prevItem
        self.hasPrev = True

    def remove(self):
        ### REMOVE IN MIDDLE OF LIST ###
        if self.hasPrev and self.hasNext:
            self.prevItem.setNext(self.nextItem)  
            del self

        ### REMOVE AT END OF LIST ###
        elif self.hasPrev and not self.hasNext:
            self.prevItem.setNext(False)
            del self

           

        


# start = pointerElement("hej")
# test2 = pointerElement(345)
# test3 = pointerElement(True)
# test4 = pointerElement(123)

# start.setNext(test2)
# test2.setNext(test3)
# test3.setNext(test4)

# test4.remove()


# def runLoop(element: pointerElement):
#     # Do actions on the element
#     print(   element.prevItem, 
#              element.item,
#              element.nextItem
#             )

#     if element.hasNext:
#         runLoop(element.nextItem)
    
# runLoop(start)

