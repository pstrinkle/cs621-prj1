"""Boring matrix model."""

from json import JSONEncoder

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

    def compute(self):
        """Run the basic term weight calculation."""
        
        # None of these are zero.
        for term in self.term_matrix:
            self.term_weights[term] = (float(self.term_matrix[term]) / self.total_count)
    
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



