import random
import glob
import sys
import traceback

"""
Markov Babbler

After being trained on text from various authors, it will
'babble' (generate random walks) and produce text that
vaguely sounds like the author of the training texts.

run as: python3 babbler.py 
or optioanlly with parameters: python3 babbler.py 2 tests/test1.txt 5 
"""

# ------------------- Implementation Details: -------------------------------
# Our entire graph is a dictionary
#   - keys/states are ngrams represented (could have been tuple, CANNOT be a list,
#       because we need to use states as dictionary keys, and lists are not hashable)
#   - values are either lists or Bags
# Starter states are a list of words (could have been a Bag; either an ordered or unordered collection, with duplicates allowed)
# When we pick a word, we transition to a new state
# e.g. suppose we are using bigrams and are at the state ‘the dog’ and we pick the word ‘runs’. 
# Our new state is ‘dog runs’, so we look up that state in our dictionary, and then get the next word, and so on…
# Ending states can generate a special "stop" symbol; we will use ‘EOL’.
#   If we generate the word ‘EOL’, then the sentence is over. Since all words are lower-case, this won’t be confused for a legitimate word

# --------------------- Tasks --------------------------------
# class Babbler:
    # def __init__(self, n, seed=None)      # already completed with initial data structures
    # def add_file(self, filename)          # already completed; calls add_sentence(), so go there next, read comments, and plan out your steps
    # def add_sentence(self, sentence)      # implement this
    # def get_starters(self)                # implement this
    # def get_stoppers(self)                # implement this
    # def get_successors(self, ngram)       # implement this
    # def get_all_ngrams(self)              # implement this
    # def has_successor(self, ngram)        # implement this
    # def get_random_successor(self, ngram) # implement this
    # def babble(self)                      # implement this

# ------------------- Tips ----------------------------------
# read through all the comments in the below functions before beginning to code
# remember that our states are n-grams, so whatever the n value is, that's how many words per state (including starters and stoppers)
# our successors (the value for each key in our dictionary) are strings representing words (not states, since n-gram states could be of multiple words)
# since we will represent your n-grams as strings, remember to separate words with a space 
# when updating your state, make sure you don't end up with extra spaces or you won't find it in the dictionary
# add print statements while debugging to ensure is step in your process is working as intended

debugging = False

class Babbler:
    
    # nothing to change here; read, understand, move along
    def __init__(self, n, seed=None):
        """
        n: length of an n-gram for state
        seed: seed for a random number generation (None by default)
        """
        self.n = n #size of our n-grams (i.e. our brain graph states will be strings of n space-separated strings)
        if seed != None: #seed:  
            random.seed(seed)

        # need to store our sparce graph as a dictionary 
        # need to store keys/states (as hashables, so strings or tuples, not list)
        # need to store values (lists or bag; both allow duplicates, one is ordered, the other is not)
            # graph = {
            #     "I think": ["therefore", this", "you", "you"],   #list of words that we've seen follow this key (preserving multiplicity)      
            # }
        # state used as keys are strings with spaces between words; values are lists of words that could follow the keys.
        # value list can have repeated entries to preserve probability


        self.brainGraph = {}  # note that we need to be able to quickly find options for current state (so we use it for indexing, i.e. as our key)

        self.starters = [] # let's track starting states as a list of strings (could have made them part of dictionary but let's have a list for debugging/testing purposes )
        # we cannot store these as part of our brain graph 
        # consider using "" as an empty state, indicating the start of a sentence
        # the list of successors would need to be entire state strings rather than just word strings as for the other states
        # this inconsistency would require special handling of the "" key in our dictionary
        # having a separate special list is a more explicit way of signaling/handling this special case

        self.stoppers = [] # let's also track ending states as a list of strings (don't really need it; only for debugging/testing purposes)
    
    # nothing to change here; read, understand, move along
    def add_file(self, filename):
        """
        This method is already done for you. 
        It processes information from all sentences in your input file, by calling add_sentence() for each line,
        after removing trailing spaces and making it lower case.
        We are assuming input data has already been pre-processed so that each sentence is on a separate line.
        """

        print("Reading from you file...")
        for line in [line.rstrip().lower() for line in open(filename, errors='ignore').readlines()]:
            self.add_sentence(line)
        print("Done reading from your file.")

        print("\n---------resulting graph: --------")
        print(self.brainGraph)
        print("----------------------------------\n")


    def add_sentence(self, sentence):
        """
        Process the given sentence (a string separated by spaces): 
        Break the sentence into words using split(); 
        Convert each word to lowercase using lower().
        Then start processing n-grams and updating your states.
        Remember to track starters (n-grams that begin sentences), stoppers (n-grams that end sentences), 
        and that any n-grams that stops a sentence should be followed by the
        special symbol 'EOL' in the state transition table. 'EOL' is short for 'end of line'; since it is capitalized and all our input texts are lower-case, it will be unambiguous.
        """
        words = sentence.lower().split()
        n = self.n
        if len(words) < n:
            return  # Not enough words for an n-gram

        # Track the starter n-gram
        starter_ngram = ' '.join(words[:n])
        self.starters.append(starter_ngram)

        # Build the n-gram graph
        for i in range(len(words) - n):
            ngram = ' '.join(words[i:i+n])
            next_word = words[i+n]
            if ngram not in self.brainGraph:
                self.brainGraph[ngram] = []
            self.brainGraph[ngram].append(next_word)

        # Handle the stopper n-gram (last n words)
        stopper_ngram = ' '.join(words[-n:])
        self.stoppers.append(stopper_ngram)
        if stopper_ngram not in self.brainGraph:
            self.brainGraph[stopper_ngram] = []
        self.brainGraph[stopper_ngram].append('EOL')

    def get_starters(self):
        """
        Return a list of all of the n-grams that start any sentence we've seen.
        The resulting list may contain duplicates, because one n-gram may start
        multiple sentences. Probably a one-line method.
        """
        return self.starters

    def get_stoppers(self):
        """
        Return a list of all the n-grams that stop any sentence we've seen.
        The resulting value may contain duplicates, because one n-gram may stop
        multiple sentences. Probably a one-line method.
        """
        return self.stoppers

    def get_successors(self, ngram):
        """
        Return a list of words that may follow a given n-gram.
        The resulting list may contain duplicates, because each
        n-gram may be followed by different words.
        If the given state never occurs, return an empty list.
        """

        return self.brainGraph.get(ngram, [])

    def get_all_ngrams(self):
        """
        Return all the possible n-grams (sequences of n words), that we have seen across all sentences.
        Probably a one-line method.
        """

        return list(self.brainGraph.keys())

    def has_successor(self, ngram):
        """
        Return True if the given ngram has at least one possible successor word, and False if it does not.
        """
        return ngram in self.brainGraph and len(self.brainGraph[ngram]) > 0

    def get_random_successor(self, ngram):
        """
        Given an n-gram, randomly pick from the possible words that could follow that n-gram.
        The randomness should take into account how likely a word is to follow the given n-gram.
        """
        successors = self.get_successors(ngram)
        if not successors:
            return None
        return random.choice(successors)

    def babble(self):
        """
        Generate a random sentence using the Markov process.
        """
        if not self.starters:
            return ""
        current_ngram = random.choice(self.starters)
        sentence = current_ngram.split()
        while True:
            next_word = self.get_random_successor(current_ngram)
            if next_word == 'EOL' or next_word is None:
                break
            sentence.append(next_word)
            # Update current_ngram to the next state (slide window)
            current_ngram = ' '.join(sentence[-self.n:])
        return ' '.join(sentence)
            

# nothing to change here; read, understand, move along
def main(n=3, filename='tests/test1.txt', num_sentences=5):
    """
    Simple test driver.
    """
    
    print('Currently running on ',filename)
    babbler = Babbler(n)
    babbler.add_file(filename)

    try:
        print(f'num starters {len(babbler.get_starters())}')
        print("\t",babbler.get_starters())
        print(f'num ngrams {len(babbler.get_all_ngrams())}')
        print(f'num stoppers {len(babbler.get_stoppers())}')
        print("\t",babbler.get_stoppers())
        print("------------------------------\nPreparing to drop some bars...\n")
        for _ in range(num_sentences):
            print(babbler.babble())
    except Exception as e:
        print("This code crashed... QQ\n"+
            " - make sure you have implemented all of the above methods\n"+
            " - review the crash report below\n"+
            " - add lots of print statements to your methods to ensure they are working as you intended\n")
        print("--------------------------Crash Report:--------------------------")
        traceback.print_exc() 

# nothing to change here; read, understand, move along
# to execute this script, in a terminal nagivate to your cs317/markov folder, unless already there
# enter the following terminal command: python3 babbler.py
# default values below will be used; alternatively you can provide up to 3 arguments (n, filename, num_sentences), for example: python3 babbler.py 2 tests/test2.txt 10
if __name__ == '__main__': 
    print("Entered arguments: ",sys.argv)
    sys.argv.pop(0) # remove the first parameter, which should be babbler.py, the name of the script
    # -------default values -----------
    n = 3
    filename = 'tests/test1.txt'
    num_sentences = 5
    #----------------------------------
    if len(sys.argv) > 0: # if any argumetns are passed, first is assumed to be n
        n = int(sys.argv.pop(0))
    if len(sys.argv) > 0: # if any more were passed, the next is assumed to be the filename
        filename = sys.argv.pop(0)
    if len(sys.argv) > 0: # if any more were passed, the next is assumed to be number of sentences to be generated 
        num_sentences = int(sys.argv.pop(0))
    main(n, filename, num_sentences) # now we call main with all the actual or default arguments