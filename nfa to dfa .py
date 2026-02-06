# -------------------------------
# Regex to NFA (Thompson's Construction)
# -------------------------------

class State:
    _id_counter = 0
    def __init__(self):
        self.id = State._id_counter
        State._id_counter += 1
        self.edges = {}   # dict: symbol -> list of states
        self.epsilon = [] # epsilon transitions

    def __repr__(self):
        edges_str = {k:[s.id for s in v] for k,v in self.edges.items()}
        eps_str = [s.id for s in self.epsilon]
        return f"State {self.id}: edges={edges_str}, epsilon={eps_str}"

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

    def describe(self):
        visited = set()
        stack = [self.start]
        description = []
        while stack:
            state = stack.pop()
            if state.id in visited:
                continue
            visited.add(state.id)
            description.append(str(state))
            for targets in state.edges.values():
                stack.extend(targets)
            stack.extend(state.epsilon)
        return "\n".join(description)

def regex_to_nfa(regex):
    # Convert regex to postfix using Shunting Yard algorithm
    def to_postfix(regex):
        precedence = {'*': 3, '.': 2, '|': 1}
        output, stack = [], []
        prev = None
        for c in regex:
            if c.isalnum():
                if prev and (prev.isalnum() or prev == ')' or prev == '*'):
                    while stack and precedence.get(stack[-1], 0) >= precedence['.']:
                        output.append(stack.pop())
                    stack.append('.')
                output.append(c)
            elif c == '(':
                if prev and (prev.isalnum() or prev == ')' or prev == '*'):
                    while stack and precedence.get(stack[-1], 0) >= precedence['.']:
                        output.append(stack.pop())
                    stack.append('.')
                stack.append(c)
            elif c == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            elif c in precedence:
                while stack and precedence.get(stack[-1], 0) >= precedence[c]:
                    output.append(stack.pop())
                stack.append(c)
            prev = c
        while stack:
            output.append(stack.pop())
        return ''.join(output)

    def build_nfa(postfix):
        stack = []
        for c in postfix:
            if c.isalnum():
                s1, s2 = State(), State()
                s1.edges[c] = [s2]
                stack.append(NFA(s1, s2))
            elif c == '.':  # concatenation
                nfa2, nfa1 = stack.pop(), stack.pop()
                nfa1.accept.epsilon.append(nfa2.start)
                stack.append(NFA(nfa1.start, nfa2.accept))
            elif c == '|':  # union
                nfa2, nfa1 = stack.pop(), stack.pop()
                s, a = State(), State()
                s.epsilon.extend([nfa1.start, nfa2.start])
                nfa1.accept.epsilon.append(a)
                nfa2.accept.epsilon.append(a)
                stack.append(NFA(s, a))
            elif c == '*':  # Kleene star
                nfa1 = stack.pop()
                s, a = State(), State()
                s.epsilon.extend([nfa1.start, a])
                nfa1.accept.epsilon.extend([nfa1.start, a])
                stack.append(NFA(s, a))
        return stack.pop()

    postfix = to_postfix(regex)
    return build_nfa(postfix)

# -------------------------------
# NFA to DFA (Subset Construction)
# -------------------------------

class DFAState:
    _id_counter = 0
    def __init__(self, nfa_states, is_accept=False):
        self.id = DFAState._id_counter
        DFAState._id_counter += 1
        self.nfa_states = frozenset(nfa_states)
        self.transitions = {}  # symbol -> DFAState
        self.is_accept = is_accept

    def __repr__(self):
        return f"DFAState({self.id}, accept={self.is_accept}, nfa_states={[s.id for s in self.nfa_states]}, transitions={ {k:v.id for k,v in self.transitions.items()} })"

def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        for eps in state.epsilon:
            if eps not in closure:
                closure.add(eps)
                stack.append(eps)
    return closure

def move(states, symbol):
    result = set()
    for state in states:
        if symbol in state.edges:
            result.update(state.edges[symbol])
    return result

def nfa_to_dfa(nfa, alphabet):
    start_closure = epsilon_closure({nfa.start})
    start_state = DFAState(start_closure, nfa.accept in start_closure)
    dfa_states = {start_state.nfa_states: start_state}
    unmarked = [start_state]

    while unmarked:
        dfa_state = unmarked.pop()
        for symbol in alphabet:
            next_states = epsilon_closure(move(dfa_state.nfa_states, symbol))
            if not next_states:
                continue
            next_states_frozen = frozenset(next_states)
            if next_states_frozen not in dfa_states:
                new_state = DFAState(next_states_frozen, nfa.accept in next_states_frozen)
                dfa_states[next_states_frozen] = new_state
                unmarked.append(new_state)
            dfa_state.transitions[symbol] = dfa_states[next_states_frozen]

    return list(dfa_states.values())

# -------------------------------
# Utility: Extract alphabet from regex
# -------------------------------
def extract_alphabet(regex):
    return set([c for c in regex if c.isalnum()])

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    regex = "(a|b)*abb"   # <-- change this to test other regexes
    alphabet = extract_alphabet(regex)

    nfa = regex_to_nfa(regex)
    print("NFA for regex:", regex)
    print("Start state:", nfa.start.id)
    print("Accept state:", nfa.accept.id)
    print("\nDetailed NFA State Transitions:")
    print(nfa.describe())

    dfa = nfa_to_dfa(nfa, alphabet)
    print("\nDFA constructed for regex:", regex)
    for state in dfa:
        print(state)
