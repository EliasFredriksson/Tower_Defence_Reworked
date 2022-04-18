class LinkedList(object):
    def __init__(self):
        self.root = None
        self.size = 0
        
    def get_size(self):
        return self.size

    def add(self, data):
        # We create a new node with the data and add it to the start of the list.
        new_node = Node(data, self.root)
        self.root = new_node
        self.size += 1

    def remove(self, data):
        # We set our current node to the root
        this_node = self.root
        # We create a variable to store the previous node
        prev_node = None
        while this_node:
            if this_node.get_data() == data:
                # If we have a privous node we set that nodes next node equal to currents next node
                if prev_node:
                    prev_node.set_next(this_node.get_next())
                else:
                # Otherwise if we dont have a previous node, we are in the root node
                    self.root = this_node
                self.size -= 1
                # We return True to indicate we successfully removed the data
                return True
            else:
                # Current node didnt contain the data we are looking for so we set previous node to current node. 
                # We advance to the next node in the list.
                prev_node = this_node
                this_node = this_node.get_next()

        # If we exit the while loop it means we didnt find the data we were looking for. So we return False.
        return False

    def find(self, data):
        this_data = self.root
        while this_data:
            # If current node contains the data we are looking for, we return the data.
            if this_data.get_data() == data:
                return data
            else:
                # Otherwise we get the next node and repeat.
                this_data = this_data.get_next()
        # If we exit the loop, it means we didnt find the data. Which we indicate by returning None
        return None

class Node(object):
    def __init__(self, data, next_node = None):
        self.data = data
        self.next_node = next_node

    def get_next(self):
        return self.next_node
    def set_next(self, next_node):
        self.next_node = next_node

    def get_data(self):
        return self.data
    def set_data(self, data):
        self.data = data

