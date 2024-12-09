#!/usr/bin/env python3

import sys
import csv
from collections import deque

# Struct or class for the tree of possible configurations
    # List of lists

# Parse Transition function
def parse_transitions(transitions_list):
    # Fill a dictionary with (state, input character to transition) as the key, and all valid transitions as values
    # Using the a+ example     key: "a" as an input character in "q1"
    #                          value: (loop back to q1, write "a", move head to the right), (transition to q2, write "a", move head to the right)
    transitions = {}
    for t in transitions_list:
        q, input_c, next_q, tape_c, direction = t
        state = (q, input_c)
        next_transition = (next_q, tape_c, direction)
        if state not in transitions:
            transitions[state] = [] # Add new state with list of possible transitions
        transitions[state].append(next_transition)  # Add new possible transition for that state

    return transitions


# Traverse NTM function with BFS
def traverse_NTM(start, accept, transitions, input_string, flag):
    
    tree = []   # Tree of possible configurations (state, tape contents, where tape head is)
    start_config = ["", start, input_string] 
    queue = deque([(start_config, 0, [start_config])])    # includes current depth
    count = 0   # keep track of transitions 
    max_depth = 0   # If all paths lead to reject, this keeps track of max steps from start to last reject

    while queue:
        current_config, depth, current_path = queue.popleft()
        max_depth = max(max_depth, depth)

        if depth >= flag:
            return False, None, count, max_depth
        
        left_tape, state, right_tape = current_config

        if state == accept:
            return True, current_path, count, depth

        if right_tape:  # checks if we have reached end of input string
            input_char = right_tape[0]
        else:
            input_char = "_"
        
        state_input = (state, input_char)
        if state_input not in transitions:
            continue    # if not a valid transition, then reject
        
        for next_q, tape_c, direction in transitions[state_input]:
            count += 1
            
            # Prepare new configuration
            new_left = left_tape
            new_right = right_tape
            
            # Write new character
            if tape_c != input_char:
                if new_right:
                    new_right = tape_c + new_right[1:]
                else:
                    new_right = tape_c
            
            # Move tape head based on direction
            if direction == 'L':
                if not new_left:
                    new_left = " "
                else:
                    new_right = new_left[-1] + new_right
                    new_left = new_left[:-1]
            elif direction == 'R':
                if not new_right:
                    new_right += " "    # Only add _ if it's the end of right side of tape
                else:
                    new_left += new_right[0]
                    new_right = new_right[1:]
            
            '''
            new_left = left_tape
            new_right = right_tape[1:]

            # Move tape head based on direction
            if direction == 'L':
                new_right = tape_c + new_right
                if new_left:
                    new_left = new_left[:1]
                    new_right = new_left[-1] + new_right
                else:
                    new_left = ""
            elif direction == 'R':
                new_left = tape_c + new_left
                if not new_right:
                    new_right = new_right + "_" # Only add _ if it's the end of right side of tape
            '''

            new_config = [new_left, next_q, new_right]

            new_path = current_path + [new_config]

            queue.append((new_config, depth + 1, new_path))
        
        tree.append(current_config)
    
    # Only reaches this point if all paths led to reject
    return False, None, count, max_depth
            
# Output function
def output(NTM_name, input_string, accept, depth, transitions_count, accepted, path, max_depth, flag):
    # name of machine
    # initial string
    # depth of tree of configurations
    # total number of transitions simulated
    print(NTM_name)
    print(f"Input_string: {input_string}")
    print(f"Depth of Config Tree: {max_depth}")
    print(f"Total Transitions: {transitions_count}")

    if accepted:
        print(f"String accepted in {len(path)-1} transitions")
        for config in path:
            left_tape, state, right_tape = config
            if state == accept:
                print(f"   {input_string}_ qacc")
                continue
            print(f"   {left_tape} {state} {right_tape[0] if right_tape else '_'}")
    elif transitions_count >= flag:
        print(f"Execution stopped after {flag} steps")
    else:
        print(f"String rejected in {max_depth} steps")


# Main function with inputs: name of file, input string, "termination" flag
def main():
    # Error check
    if len(sys.argv) < 4:
        print("Invalid Command Line Arguments")
        sys.exit(1)

    # Command Line arguments
    NTM_file = sys.argv[1]
    input_string = sys.argv[2]
    flag = int(sys.argv[3])

    # open file and parse info
    with open(sys.argv[1], 'r') as file:
        reader = csv.reader(file)
        NTM = list(reader)

        # Assign values from csv file describing NTM
        NTM_name = NTM[0][0]    # Name of machine
        Q = NTM[1]              # State names
        sigma = NTM[2]          # Input characters
        gamma = NTM[3]          # Tape characters
        start = NTM[4][0]       # Start state
        accept = NTM[5][0]      # Accept state
        reject = NTM[6][0]      # Reject state
        transitions_list = NTM[7:]   # Valid transitions
    
    transitions = parse_transitions(transitions_list)   # Parse transition function

    accepted, path, transitions_count, max_depth = traverse_NTM(start, accept, transitions, input_string, flag)

    if path:
        depth = len(path)
    else:
        depth = 0

    output(NTM_name, input_string, accept, depth, transitions_count, accepted, path, max_depth, flag)

    for line in sys.stdin:
        input_string = line.strip()
        accepted, path, transitions_count, max_depth = traverse_NTM(start, accept, transitions, input_string, flag)

        if path:
            depth = len(path)
        else:
            depth = 0

        output(" ", input_string, accept, depth, transitions_count, accepted, path, max_depth, flag)
        print()




if __name__ == '__main__':
    main()
