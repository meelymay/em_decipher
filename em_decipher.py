import sys, random

alphabet = 'abcdefghijklmnopqrstuvwxyz'
# alphabet = 'abcde'

def generate_encoding():
    encoding = {}
    alpha_copy = [x for x in alphabet]
    for i in range(len(alphabet)):
        x = alpha_copy[int(random.random()*len(alpha_copy))]
        encoding[alphabet[i]] = x
        alpha_copy.remove(x)
    return encoding

def encode(s, encoding):
    return reduce(lambda x,y: x+y, [(encoding[x] if (x in encoding) else ' ')  for x in s])

def calc_word_prob(plain_word, code_word, letter_probs):
    if len(plain_word) != len(code_word):
        return 0

    prob = 1
    for i in range(len(plain_word)):
        prob *= letter_probs[plain_word[i]][code_word[i]]

    return prob

def normalize_counts(letter_counts):
    letter_probs = {}
    for plain_letter in letter_counts:
        total = 0
        letter_probs[plain_letter] = {}
        for code_letter in letter_counts[plain_letter]:
            total += letter_counts[plain_letter][code_letter]

        for code_letter in letter_counts[plain_letter]:
            letter_probs[plain_letter][code_letter] = letter_counts[plain_letter][code_letter]/total if total != 0 else 0
    return letter_probs

def add_letter_counts(plain_word, code_word, word_probs, letter_counts):
    if len(plain_word) != len(code_word):
        return 0

    for i in range(len(plain_word)):    
        letter_counts[plain_word[i]][code_word[i]] = letter_counts[plain_word[i]][code_word[i]] + word_probs[plain_word][code_word]

def copy_probs(probs):
    new_probs = {}
    for p1 in probs:
        new_probs[p1] = {}
        for p2 in probs:
            new_probs[p1][p2] = probs[p1][p2]*1
    return new_probs

def empty_letter_counts():
    probs = {}
    for p1 in alphabet:
        probs[p1] = {}
        for p2 in alphabet:
            probs[p1][p2] = 0
    return probs

def initialize(plain_words, letter_probs, old_letter_probs, word_probs):
    init_prob = 1/float(len(alphabet))
    for l1 in alphabet:
        letter_probs[l1] = {}
        old_letter_probs[l1] = {}
        old_letter_probs[l1][l1] = 1.0
        for l2 in alphabet:
            letter_probs[l1][l2] = init_prob
            if l1 != l2:
                old_letter_probs[l1][l1] = 0.0

    for word in plain_words:
        word_probs[word] = {}

def converged(p1, p2):
    epsilon = .0001
    for l1 in p1:
        for l2 in p1[l1]:
            diff = p1[l1][l2] - p2[l1][l2]
            if abs(diff) > epsilon:
                return False
    return True

def show_probs(probs, show_all=False):
    for x in probs:
        print x,'->'
        for y in probs[x]:
            p = probs[x][y] 
            if p > .1 or show_all:
                print '\t',y,'\t',p

def get_decoding_from_probs(probs):
    decoding = {}
    for l in probs:
        decoding[l] = max([x for x in probs[l]], key=lambda x: probs[l][x])
    return decoding

def em(plain_words, code_words):
    letter_probs = {}
    old_letter_probs = {}
    word_probs = {}
    initialize(plain_words, letter_probs, old_letter_probs, word_probs)

    iterations = 0
    while not converged(letter_probs, old_letter_probs):
        iterations += 1

        # copy to old_letter_probs
        old_letter_probs = copy_probs(letter_probs)

        # expectation: get probabilities of words
        for plain_word in plain_words:
            for code_word in code_words:
                word_probs[plain_word][code_word] = calc_word_prob(plain_word, 
                                                                   code_word,
                                                                   letter_probs)


        # maximization: get weighted counts of letters, normalize
        letter_counts = empty_letter_counts()
        for plain_word in plain_words:
            for code_word in code_words:
                add_letter_counts(plain_word,
                                  code_word, 
                                  word_probs, 
                                  letter_counts)
        letter_probs = normalize_counts(letter_counts)
                
    # show_probs(letter_probs)
    # show_probs(word_probs)

    decoding = get_decoding_from_probs(letter_probs)

    print 'iterations:',iterations
    return decoding

# toy example
#    alphabet = 'abcde'
#    plain_text = 'cab bad bed dabbed ace add abe bead ab'

if __name__ == '__main__':
    
    corpus = 'piotr is a doof butt but amelias butt smells better because she smells like flowers dogs are doofs and they smell each others butts of named the dog'
    
    plain_text = 'a dog named amelia smells the butt of a doof piotr'
    encoding = generate_encoding()
    code_text = encode(plain_text, encoding)

    print plain_text
    print code_text

    plain_words = set(corpus.split())
    code_words = set(code_text.split())

    decoding = em(code_words, plain_words)
    
    deciphered_text = encode(code_text, decoding)
    print deciphered_text
