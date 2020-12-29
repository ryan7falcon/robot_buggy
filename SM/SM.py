class SM:
    start_state = None
    def start(self):
        self.state = self.start_state

    def step(self, inp=None):
        (next_state, output) = self.get_next_values(self.state, inp)
        self.state = next_state
        return output

    def get_next_values(self, state, inp):
            next_state = self.get_next_state(state, inp)
            return (next_state, next_state)

    def transduce(self, inputs):
        self.start()
        result = []
        for inp in inputs:
            result.append(self.step(inp))
            if self.done(self.state):
                break
        return result

    def run(self, n = 10):
        return self.transduce([None]*n)
        
    def done(self, state):
        return False
    
    def get_start_state(self):
        return self.start_state
        
class Parallel(SM):
    def __init__(self, sm1, sm2):
        self.m1 = sm1
        self.m2 = sm2
        self.start_state = (sm1.start_state, sm2.start_state)
        self.start()
        
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.get_next_values(s1, inp)
        (new_s2, o2) = self.m2.get_next_values(s2, inp)
        return ((new_s1, new_s2), (o1, o2))
        
class Cascade(SM):
    def __init__(self, sm1, sm2):
        self.m1 = sm1
        self.m2 = sm2
        self.start_state = (sm1.start_state, sm2.start_state)
        self.start()
        
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.get_next_values(s1, inp)
        (new_s2, o2) = self.m2.get_next_values(s2, o1)
        return ((new_s1, new_s2), o2)

def split_value(v):
    if v == "undefined":
        return ("undefined", "undefined")
    else:
        return v
        
class Parallel2(Parallel):
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (i1, i2) = split_value(inp)
        (new_s1, o1) = self.m1.get_next_values(s1, i1)
        (new_s2, o2) = self.m2.get_next_values(s2, i2)
        return ((new_s1, new_s2), (o1, o2))
        
class ParallelAdd(Parallel):
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.get_next_values(s1, inp)
        (new_s2, o2) = self.m2.get_next_values(s2, inp)
        return ((new_s1, new_s2), o1 + o2)
        
class Wire(SM):
    def get_next_state(self, state, inp):
        return inp
        
class Delay(SM):
    def __init__(self, v0):
        self.start_state = v0
    def get_next_values(self, state, inp):
        return (inp, state) # input becomes new state, and output is old state
        
class Feedback (SM):
    def __init__(self, sm):
        self.m = sm
        self.start_state = self.m.start_state
        self.start()
        
    def get_next_values(self, state, inp):
        (ignore, o) = self.m.get_next_values(state, "undefined")
        (new_s, ignore) = self.m.get_next_values(state, o)
        return (new_s, o)
    
class Feedback2(Feedback):
    def get_next_values(self, state, inp):
        (ignore, o) = self.m.get_next_values(state, (inp, "undefined"))
        (new_s, ignore) = self.m.get_next_values(state, (inp, o))
        return (new_s, o)
        
class FeedbackAdd(Feedback):
    def get_next_values(self, state, inp):
        (ignore, o) = self.m.get_next_values(state, "undefined")
        (new_s, ignore) = self.m.get_next_values(state, inp + o)
        return (new_s, o)

class FeedbackSubtract(Feedback):
    def get_next_values(self, state, inp):
        (ignore, o) = self.m.get_next_values(state, "undefined")
        (new_s, ignore) = self.m.get_next_values(state, inp - o)
        return (new_s, o)
        

# eval condition on input, update the state of one of the machines
class Switch(SM):
    def __init__(self, condition, sm1, sm2):
        self.m1 = sm1
        self.m2 = sm2
        self.condition = condition
        self.start_state = (sm1.start_state, sm2.start_state)
        self.start()
        
    def get_next_values(self, state, inp):
        (s1, s2) = state
        if self.condition(inp):
            (ns1, o) = self.m1.get_next_values(s1, inp)
            return ((ns1, s2), o)
        else:
            (ns2, o) = self.m2.get_next_values(s2, inp)
            return ((s1, ns2), o)
        
# same as switch, but update both machines, choose 1 output
class Mux (Switch):
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (ns1, o1) = self.m1.get_next_values(s1, inp)
        (ns2, o2) = self.m2.get_next_values(s2, inp)
        if self.condition(inp):
            return ((ns1, ns2), o1)
        else:
            return ((ns1, ns2), o2)     

# based on condition, forever execute one of the machines
class If (SM):
    start_state = ('start', None)
    def __init__(self, condition, sm1, sm2):
        self.sm1 = sm1
        self.sm2 = sm2
        self.condition = condition
        self.start()
        
    def get_first_real_state(self, inp): 
        if self.condition(inp):
            return ('runningM1', self.sm1.start_state) 
        else:
            return ('runningM2', self.sm2.start_state)
            
    def get_next_values(self, state, inp):
        (ifState, sm_state) = state
        if ifState == 'start':
            (ifState, sm_state) = self.get_first_real_state(inp)
        if ifState == 'runningM1':
            (newS, o) = self.sm1.get_next_values(sm_state, inp)
            return (('runningM1', newS), o)
        else:
            (newS, o) = self.sm2.get_next_values(sm_state, inp)
            return (('runningM2', newS), o)
            
class Repeat(SM):
    def __init__(self, sm, n = None):
        self.sm = sm
        self.start_state = (0, self.sm.start_state)
        self.n = n
        self.start()
        
    def advance_if_done(self, counter, sm_state):
        while self.sm.done(sm_state) and not self.done((counter, sm_state)):
            counter = counter + 1
            sm_state = self.sm.start_state
        return (counter, sm_state)    

    def get_next_values(self, state, inp):
        (counter, sm_state) = state
        (sm_state, o) = self.sm.get_next_values(sm_state, inp)
        (counter, sm_state) = self.advance_if_done(counter, sm_state)
        return ((counter, sm_state), o)
        
    def done(self, state):
        (counter, sm_state) = state
        return counter == self.n
    
# run each machine util its done, then go to next
class Sequence (SM):
    def __init__(self, sm_list):
        self.sm_list = sm_list
        self.start_state = (0, self.sm_list[0].start_state)
        self.n = len(sm_list)
    

    def advance_if_done(self, counter, sm_state):
        while self.sm_list[counter].done(sm_state) and counter + 1 < self.n:
            counter = counter + 1
            sm_state = self.sm_list[counter].start_state
        return (counter, sm_state)


    def get_next_values(self, state, inp):
        (counter, sm_state) = state
        (sm_state, o) = self.sm_list[counter].get_next_values(sm_state, inp)
        (counter, sm_state) = self.advance_if_done(counter, sm_state)
        return ((counter, sm_state), o)

    def done(self, state):
        (counter, sm_state) = state
        return self.sm_list[counter].done(sm_state)

# will restart the machine until the condition is true when machine is done
class RepeatUntil (SM):
    def __init__(self, condition, sm):
        self.sm = sm
        self.condition = condition
        self.start_state = (False, self.sm.start_state)
        
    def get_next_values(self, state, inp):
        (cond_true, sm_state) = state
        (sm_state, o) = self.sm.get_next_values(sm_state, inp)
        cond_true = self.condition(inp)
        if self.sm.done(sm_state) and not cond_true:
            sm_state = self.sm.get_start_state()
        return ((cond_true, sm_state), o)
    
    def done(self, state):
        (cond_true, sm_state) = state
        return self.sm.done(sm_state) and cond_true

# will continue running the machine until the condition is true at any step of the execution - then stop
class Until (SM):
    def __init__(self, condition, sm):
        self.sm = sm
        self.condition = condition
        self.start_state = (False, self.sm.start_state)
        
    def get_next_values(self, state, inp):
        (cond_true, sm_state) = state
        (sm_state, o) = self.sm.get_next_values(sm_state, inp)
        cond_true = self.condition(inp)
        return ((cond_true, sm_state), o)
    
    def done(self, state):
        (cond_true, sm_state) = state
        return cond_true or self.sm.done(sm_state)