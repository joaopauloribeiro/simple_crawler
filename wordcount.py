'''
Created on Aug 28, 2011

@author: lordzeus
'''

import sys

def parse_file(filename):
    def clean_text(text):
        ponctuation = ',.;:~^]}[{=+-_()<>|\\/*&%$#@!"'
        for char in ponctuation:
            text = text.replace(char, ' ')
        return text
    def remove_preposition(text):
        preposition = ['the', 'and', 'of', 'to', 'I', 'you', 'a', 'my', 'in', 'HAMLET', 'it', 'is', 'not', 'his', 'And', 'that', 'this', 'your', 'me', 'with', 'be', 'him', 'for', 'lord', 'he', 'have', 'but', 'as', 'will', 'The']
        for word in preposition:
            word_count = text.count(word)
            for i in range(word_count):
                 text.remove(word)
        return text
    file = open(filename, 'rU', encoding='latin-1')
    file_text = file.read()
    file_words = clean_text(file_text).replace('\n', ' ').split()
    #file_words = remove_preposition(file_words)
    return file_words

def word_count(text_words):
    words_count = {}
    for word in text_words:
        if word not in words_count:
            words_count[word] = 1
        else:
            words_count[word] += 1
    return words_count

def top_words(limit, words_count):
    def count(word_tuple):
        return (word_tuple[1])
    sorted_word_count = sorted(words_count.items(), key=count, reverse=True)
    top_words_count = []
    if limit == -1:
        sorted_word_count = sorted_word_count[:30]
    for tupple in sorted_word_count:
        if tupple[1] > limit:
            top_words_count.append(tupple)
    return top_words_count

def main():
    if len(sys.argv) == 1:
        print("usage:\n", sys.argv[0], " filename [--top [limit]] [-t]")
    else:
        print(sys.argv[1:])
        file_parsed = parse_file(sys.argv[1])
        word_ranking = word_count(file_parsed)
        if len(sys.argv) == 3:
            word_ranking = top_words(-1, word_ranking)
        elif len(sys.argv) >= 4:
            word_ranking = top_words(int(sys.argv[3]), word_ranking)

        total_word_count = 0
        words_list = []
        for word_tupple in word_ranking:
            if len(sys.argv) >= 3:
                total_word_count += word_tupple[1]
                print(word_tupple[0], ':', word_tupple[1])
            else:
                print(word_tupple)
            words_list.append(word_tupple[0])

        print(words_list)
        if len(sys.argv) == 5:
            print("Total Word Count:",total_word_count)

if __name__ == '__main__':
    main()
