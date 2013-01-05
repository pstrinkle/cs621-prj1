"""Boring matrix model."""

from json import JSONEncoder
from datetime import datetime

from math import sqrt

def datetime_from_long(timestamp):
    """Convert a timestamp to a datetime.datetime."""

    timeasstr = str(timestamp)

    year = int(timeasstr[0:4])
    month = int(timeasstr[4:6])
    day = int(timeasstr[6:8])
    hour = int(timeasstr[8:10])
    minute = int(timeasstr[10:12])
    second = int(timeasstr[12:14])

    return datetime(year, month, day, hour, minute, second)

def long_from_datetime(dto):
    """Convert a datetime object to an integer."""
    
    return int(dto.strftime("%Y%m%d%H%M%S"))

def localclean(text):
    """Locally clean the stuff, replace #'s and numbers."""
    
    neat = text.replace("#", " ")
    neat = neat.replace("$", " ")
    neat = neat.replace("`", " ")
    neat = neat.replace("%", " ")
    
    neat = neat.replace("0", " ")
    neat = neat.replace("1", " ")
    neat = neat.replace("2", " ")
    neat = neat.replace("3", " ")
    neat = neat.replace("4", " ")
    neat = neat.replace("5", " ")
    neat = neat.replace("6", " ")
    neat = neat.replace("7", " ")
    neat = neat.replace("8", " ")
    neat = neat.replace("9", " ")
    
    neat = neat.replace("-", "")
    
    return neat

class BoringMatrix():
    """This is a boring matrix."""

    def get_json(self):
        dct = {"__BoringMatrix__" : True}
        dct["matrix"] = self.term_matrix
        dct["weights"] = self.term_weights
        dct["count"] = self.total_count
        
        return dct

    def __init__(self, bag_of_words):
        """Initialize this structure with a long string."""
        
        self.term_matrix = {}
        self.term_weights = {}
        self.total_count = 0
        self.add_bag(bag_of_words)

    def drop_not_in(self, terms):
        """Drops all terms not in terms."""

        drop = []

        for term in self.term_matrix:
            if term not in terms:
                drop.append(term)

        for term in drop:
            del self.term_matrix[term]
            self.total_count -= 1

            try:
                del self.term_weights[term]
            except KeyError:
                pass

    def drop_singles(self):
        """Drops out the singles."""
        
        drop = []
        
        for term in self.term_matrix:
            if self.term_matrix[term] == 1:
                drop.append(term)
        
        for term in drop:
            del self.term_matrix[term]
            self.total_count -= 1
            
            try:
                del self.term_weights[term]
            except KeyError:
                pass

    def greater_than_one(self):
        """Returns the number of terms whose counts are greater than 1."""

        return sum([1 for term in self.term_matrix if self.term_matrix[term] > 1]) 

    def compute(self):
        """Run the basic term weight calculation."""

        #print (len(self.term_matrix), self.total_count)

        # None of these are zero.
        for term in self.term_matrix:
            self.term_weights[term] = (float(self.term_matrix[term]) / self.total_count)

    def counts_magnitude(self):
        """Compute the magnitude."""
        
        weight = 0.0

        for term in self.term_matrix:
            weight += (self.term_matrix[term] * self.term_matrix[term])
        
        return sqrt(weight)

    def weights_magnitude(self):
        """Compute the magnitude --- assumes you've already called compute()."""
        
        weight = 0.0

        for term in self.term_matrix:
            weight += (self.term_weights[term] * self.term_weights[term])
        
        return sqrt(weight)
    
    def build_fulllist(self, full_terms):
        """Return a list of term frequencies where anything absent is 0.
        
        Consider having this build a list of tuples which includes the index."""

        full_list = []

        for term in full_terms:
            if term in self.term_matrix:
                full_list.append(self.term_matrix[term])
            else:
                full_list.append(0)

        return full_list

    def add_bag(self, bag_of_words):
        """Add a bag of words to the current matrix."""
        
        if bag_of_words is None:
            return
        
        for word in bag_of_words.split(" "):
            try:
                self.term_matrix[word] += 1
            except KeyError:
                self.term_matrix[word] = 1
            self.total_count += 1

def as_boring(dct):
    """Build a boring object from a dictionary from a boring matrix."""
    if '__BoringMatrix__' in dct:
        x = BoringMatrix(None)
        x.term_matrix = dct["matrix"]
        x.term_weights = dct["weights"]
        x.total_count = dct["count"]
        return x
    return dct

class BoringMatrixEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BoringMatrix):
            return obj.get_json()
        return JSONEncoder.default(self, obj)

def boring_count_similarity(boring_a, boring_b):
    """Return the count-based cosine similarity given the two term_matrices."""
    
    count = 0.0
    
    if len(boring_a.term_matrix) == 0 or len(boring_b.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            count += boring_a.term_matrix[term] * boring_b.term_matrix[term]
            
    return float(count / (boring_a.counts_magnitude() * boring_b.counts_magnitude())) 

def boring_weight_similarity(boring_a, boring_b):
    """Return the weight-based cosine similarity given the two term_matrices."""
    
    weight = 0.0

    if len(boring_a.term_matrix) == 0 or len(boring_b.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            weight += boring_a.term_weights[term] * boring_b.term_weights[term]
            
    return float(weight / (boring_a.weights_magnitude() * boring_b.weights_magnitude()))

def dump_weights_matrix(term_dict, dict_of_boring, delimiter = ","):
    """Given a set of terms and a dictionary of boring, return the matrix."""
    
    output = ""
  
    sorted_docs = sorted(dict_of_boring.keys())  
    sorted_terms = sorted(term_dict)
  
    # Print Term Rows
    for term in sorted_terms:
        row = []
        for doc in sorted_docs:

            if term in dict_of_boring[doc].term_weights:
                row.append(str(dict_of_boring[doc].term_weights[term]))
            else:
                row.append(str(0.0))

        output += delimiter.join(row)
        output += "\n"

    return output

class HierarchBoring():
    """This builds a hierarchical version of the model given two BoringMatrix
    unigram language models."""
    
    def __init__(self, boringmatrix_a, boringmatrix_b):
        """Initialize the hierarchical model given two boring matrix."""

        # global variables.
        self.term_matrix = {}
        self.term_weights = {}
        self.total_count = 0

        self.boring_a = BoringMatrix(None)
        self.boring_a.term_matrix = boringmatrix_a.term_matrix.copy()
        self.boring_a.term_weights = boringmatrix_a.term_weights.copy()
        self.boring_a.total_count = boringmatrix_a.total_count

        self.boring_b = BoringMatrix(None)
        self.boring_b.term_matrix = boringmatrix_b.term_matrix.copy()
        self.boring_b.term_weights = boringmatrix_b.term_weights.copy()
        self.boring_b.total_count = boringmatrix_b.total_count        
        
        #print (len(self.boring_a.term_matrix), self.boring_a.total_count,
        #       len(self.boring_b.term_matrix), self.boring_b.total_count)
        
        deletes = []
        
        for akey in self.boring_a.term_matrix:
            if akey in self.boring_b.term_matrix:
                akey_count = (self.boring_a.term_matrix[akey] + self.boring_b.term_matrix[akey])
                
                self.term_matrix[akey] = akey_count
                self.total_count += akey_count
                
                # in both
                self.boring_a.total_count -= self.boring_a.term_matrix[akey]
                self.boring_b.total_count -= self.boring_b.term_matrix[akey]
            else:
                self.boring_a.total_count -= self.boring_a.term_matrix[akey]
                deletes.append(akey) # in A but not in B.

        for bkey in self.boring_b.term_matrix:
            if bkey not in self.boring_a.term_matrix:
                self.boring_b.total_count -= self.boring_b.term_matrix[bkey]
                if bkey not in deletes: # to avoid duplicates.
                    deletes.append(bkey)
                
        for delete in deletes:
            try:
                del self.boring_a.term_matrix[delete]
            except KeyError:
                pass
                
            try:
                del self.boring_a.term_weights[delete]
            except KeyError:
                pass
                
            try:
                del self.boring_b.term_matrix[delete]
            except KeyError:
                pass
                
            try:
                del self.boring_b.term_weights[delete]
            except KeyError:
                pass

    def compute(self):
        """Run the basic term weight calculation."""

        # None of these are zero.
        for term in self.term_matrix:
            self.term_weights[term] = (float(self.term_matrix[term]) / self.total_count)

        #self.boring_a.compute()
        #self.boring_b.compute()

