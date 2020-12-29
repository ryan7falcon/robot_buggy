from SM.SM import SM, Sequence

class CharTSM (SM): 
    start_state = False
    def __init__(self, c):
        self.c = c
    def get_next_values(self, state, inp):
        return (True, self.c)
    def done(self, state):
        return state

class Select (SM):
    def __init__(self, k):
        self.k = k
        self.start()
        
    def get_next_state(self, state, inp):
        return inp[self.k]
    
class Gain(SM):
    def __init__(self, k):
        self.k = k
        self.start()
        
    def get_next_state(self, state, inp):
        return inp * self.k
        
class Accumulator(SM):
    def __init__(self, initial_value):
        self.start_state = initial_value
        self.start()
        
    def get_next_state(self, state, inp):
        return state + inp, state + inp

def safe_add(a,b):
    if a and b:
        return a + b
    if a:
        return a
    if b:
        return b
    
class Increment(SM):
    def __init__(self, incr):
        self.incr = incr
        self.start()
        
    def get_next_state(self, state, inp):
        return safe_add(inp, self.incr)      

class BoolCounter(SM):
    start_state = 0
    def __init__(self):
        self.start()

    def get_next_values(self, state, inp):
        if inp:
            state += 1
            return (state, state)
        return (state, None)

def make_text_sequenceTSM(str): 
    return Sequence([CharTSM(c) for c in str]) 

class ConsumeFiveValues(SM):
    start_state = (0, 0)       # count, total
    def get_next_values(self, state, inp):
        (count, total) = state
        if count == 4:
            return ((count + 1, total + inp), total + inp)
        else:
            return ((count + 1, total + inp), None)
        
    def done(self, state):
        (count, total) = state
        return count == 5