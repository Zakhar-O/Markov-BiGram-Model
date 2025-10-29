import random

corpus = input("Insert a corpus: ")
puncts = [" ",".",";",",","!","?","\n","\"","'",":"]
word_bag = {"<UNK>":0}
s = ""
amount = 0
for c in corpus:
    if c in puncts: #word border
        if not s == "":
            value_s = word_bag.get(s, 0)
            word_bag[s]= value_s+1
            s = ""
            amount += 1
        if not c == " " and not c == "\n":
            value_c = word_bag.get(c, 0)
            word_bag[c]= value_c+1
            amount +=1
    else:
        s = s+c.lower()
        
try:
    if not corpus[-1] in puncts: #guardrail in case punctuation is missing
        value_s = word_bag.get(s, 0)
        word_bag[s] = value_s+1
        amount += 1
        s = ""
except IndexError: #We allow an empty corpus just for fun :)
    pass

prob_uni_bag = dict()
alphabet_len = len(list(word_bag))
#unigram probabilites
for word, quant in word_bag.items():  
    prob_uni_bag[word] = (quant+1)/(amount+alphabet_len) #laplace smoothing

prob_bi_bag = dict()

unk_list = dict()
for u in list(word_bag):
    unk_list[u] = 0
prob_bi_bag["<UNK>"] = unk_list

prev = ""
current = ""
barrier = True

#bigram probabilities
for i in corpus:
    if i in puncts: #word border
        if prev == "" and current == "": #boolean requirement for the strange case in which the first letter is a punctuation
            current = i
        if not current == "": 
            if barrier == True:
                barrier = False
                prev = current
                current = ""
                continue
            elif barrier == False:
                dicty = prob_bi_bag.get(prev, None)
                if dicty == None:
                    temporary = dict()
                    for w in list(word_bag):
                        if w == current:
                            temporary[w] = 1
                        else:
                            temporary[w] = 0
                    prob_bi_bag[prev] = temporary
                    prev = current
                    current = ""
                else:
                    seen = dicty.get(current, 0)
                    dicty[current] = seen+1
                    prev = current
                    current = ""

        if not i == " " and not i == "\n":
            dicty = prob_bi_bag.get(prev, None)
            if dicty == None:
                temporary = dict()
                for w in list(word_bag):
                    if w == i:
                        temporary[w] = 1
                    else:
                        temporary[w] = 0
                    prob_bi_bag[prev] = temporary
                prev = i
            else:
                seen = dicty.get(i, 0)
                dicty[i] = seen+1
                prev = i

    else:
        current = current+i.lower()


for req, probs in prob_bi_bag.items():
    new_dict = dict()
    for suc, p in probs.items():
        value = (p+1)/(word_bag[req]+alphabet_len) #laplace smoothing
        #value = p/word_bag[req] #variant without smoothing
        new_dict[suc] = value
        prob_bi_bag[req] = new_dict

print("Corpus processed")
print("---------")

while True:
    print("Type '@PREDICT' to predict the next word")
    print("Type '@EVALUATE' to determine the best sequence")
    print("Type '@EXIT' to terminate the program")
    mode = input()
    if mode == "@PREDICT":
        while True:
            foundation = input("Enter an unfinished sentence: ")
            if foundation == "@EXIT":
                break
            elif foundation == "": #special case where the user enters no string
                uni_vals = prob_uni_bag.copy() #a clone of the unigram probs
                uni_val = None
                words = set(list(word_bag)) #all words in the corpus
                words.discard("<UNK>")
                if words.issubset(set(puncts)): #if the corpus only contains punctuations, we allow punctuations to be at the beginning
                    uni_val = max(uni_vals, key=uni_vals.get)
                    if uni_val == "<UNK>" and words == set(): #If only the pseudo-word exists, it is replaced with an empty string
                        uni_val = ""
                    elif uni_val == "<UNK>" and words != set(): #else the next best choice is picked
                        del uni_vals["<UNK>"]
                        uni_val = max(uni_vals, key=uni_vals.get)
                    print(uni_val + " ")
                else:
                    while True:
                        uni_val = max(uni_vals, key=uni_vals.get)
                        if uni_val in puncts and uni_val not in ["'","\""] or uni_val == "<UNK>": #Sentences usually don't start with punctuations, which is why most of them are excluded here, along with the unknown word
                            del uni_vals[uni_val]
                        else:
                            print(uni_val + " ")
                            break
            else: #normal operation           
                tokens = []
                tok = ""
                for b in foundation:
                    if b in puncts:
                        if not tok == "":
                            tokens.append(tok)
                            tok = ""
                        if not b == " ":
                            tokens.append(b)
                    else:
                        tok = tok+b.lower()

                if not foundation[-1] in puncts: #captures the last word if no punctuation provided
                        tokens.append(tok)

                if tokens == []:
                    tokens.append("<UNK>") #renders the last token as unknown in case no tokens could be identified

                final = tokens[-1]
                best_val = 0
                w_choice = None
                possibilites = prob_bi_bag.get(final,None)
                if possibilites == None:
                    possibilites = prob_bi_bag["<UNK>"] #all unseen words are unified under the pseudoword <UNK>
                
                choices = {1:""}
                for pos, val in possibilites.items(): #The last tokens possible successors are looked at, those with the highest probability are put into a dictionary
                    if val > best_val and str(pos)!= "<UNK>":
                        best_val = val
                        if len(list(choices)) != 1:
                            choices = {1:""} #the dictionary is reset if a better word is found, to avoid worse words staying as a choice
                        choices[1] = str(pos)
                    elif val == best_val and val != 0 and str(pos)!= "<UNK>": #special case where the probability is equal
                        index = len(list(choices))+1
                        choices[index] = str(pos)
                    else:
                        continue
                
                if len(list(choices)) == 1:
                    w_choice = choices[1]
                else:
                    w_choice = random.choice(list(choices.values())) #If there is more than one "best choice", one of the best tokens is chosen randomly
                    
                if w_choice in puncts:
                    print(foundation + w_choice + " ")
                else:
                    print(foundation + " " + w_choice)
        
    elif mode == "@EVALUATE":
        while True:
            s1 = input("Enter a sentence: ")
            if s1 == "@EXIT":
                break
            elif s1 == "" or s1.strip(" ") == "": #We do not allow empty inputs or inputs only consisting of spaces
                continue
            s2 = input("Enter another sentence: ")
            if s2 == "@EXIT":
                break
            elif s2 == "" or s2.strip(" ") == "":
                continue

            tokens_1 = []
            tokens_2 = []
            
            t1 = ""
            for b1 in s1:
                if b1 in puncts:
                    if not t1 == "":
                        tokens_1.append(t1)
                        t1 = ""
                    if not b1 == " " and not b1 == "\n":
                        tokens_1.append(b1)
                else:
                    t1 = t1 + b1.lower()

            if not s1[-1] in puncts:
                tokens_1.append(t1)
                t1 = ""
                
            t2 = ""
            for b2 in s2:
                if b2 in puncts:
                    if not t2 == "":
                        tokens_2.append(t2)
                        t2 = ""
                    if not b2 == " " and not b2 == "\n":
                        tokens_2.append(b2)
                else:
                    t2 = t2 + b2.lower()
            
            if not s2[-1] in puncts:
                tokens_2.append(t2)
                t2 = ""

            prob_1 = 1 #the product of all n-grams of the first sentence
            prob_2 = 1 #the product of all n-grams of the second sentence
            gatekeep_1 = True
            gatekeep_2 = True
            require = ""
            for w1 in tokens_1:
                if gatekeep_1 == True:
                    gatekeep_1 = False
                    pp = prob_uni_bag.get(w1, None) #the first token is the unigram probability
                    if pp == None:
                        pp = prob_uni_bag.get("<UNK>",0)
                    prob_1 = prob_1*pp
                    require = w1
                else:
                    pps = prob_bi_bag.get(require, None)
                    if pps == None:
                        pps = prob_bi_bag.get("<UNK>",0)
                    pp = pps.get(w1,None)
                    if pp == None:
                        pp = pps.get("<UNK>",0)
                    prob_1 = prob_1*pp
                    require = w1
                
            require = ""

            for w2 in tokens_2:
                if gatekeep_2 == True:
                    gatekeep_2 = False
                    pp = prob_uni_bag.get(w2, None)
                    if pp == None:
                        pp = prob_uni_bag.get("<UNK>",0)
                    prob_2 = prob_2*pp
                    require = w2
                else:
                    pps = prob_bi_bag.get(require, None)
                    if pps == None:
                        pps = prob_bi_bag.get("<UNK>",0)
                    pp = pps.get(w2,None)
                    if pp == None:
                        pp = pps.get("<UNK>",0)
                    prob_2 = prob_2*pp
                    require = w2
                
            root1 = 1/len(tokens_1)
            root2 = 1/len(tokens_2)
            perplexity1 = (1/prob_1)**root1 #perplexity normalizes the value regardless of sentence length
            perplexity2 = (1/prob_2)**root2

            if perplexity1 < perplexity2:
                print("\"{}\" has a higher probability.".format(s1))
            elif perplexity2 < perplexity1:
                print("\"{}\" has a higher probability.".format(s2))
            else:
                print("The sequences have an identical probability.")


    elif mode == "@EXIT":

        break
