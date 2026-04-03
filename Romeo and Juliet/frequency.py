from romeo_and_juliet import PLAY
import copy


# Print the first 1000 characters of the play, you can remove this print
# print(PLAY[:1000])

def clean_text(text):
    # Is there a better way?
    #cleaned_text = text.replace(".", " ")
    #cleaned_text = cleaned_text.replace("_]", "")
    #cleaned_text = cleaned_text.replace("[_", "")
    #cleaned_text = cleaned_text.replace("\n", " ")
    #cleaned_text = cleaned_text.replace(":", " ")
    #cleaned_text = cleaned_text.replace(",", " ")
    #cleaned_text = cleaned_text.replace("?", " ")
    #cleaned_text = cleaned_text.replace("!", " ")
    trans_table=text.maketrans("\n:?!.,_[]","         ")
    cleaned_text=text.translate(trans_table)
    #print(cleaned_text)
    return cleaned_text


def get_words(text):
    words_in_text = text.split()
    # lower all the words in the list using list comprehension
    words_in_text = [x.lower() for x in words_in_text]
    return words_in_text


def words_frequency(words):
    play_dict = {}
    for word in words:
        if word not in play_dict:
            play_dict[word] = 0
        play_dict[word] += 1
    return play_dict


def top_n_words(freq, n):
    # To maintain a clean working function:
    # keep the original dictionary in tact

    play_dict = copy.deepcopy(freq)
    top_n_list = []
    most_frequent_words = [] #there could be a tie in most frequent words, therefor most frequent words are stored in a list
    for top_n in range(n):
        highest_frequency = 0
        most_frequent_words.clear()
        nr_of_ties=0
        for mfw, hf in play_dict.items():
            if hf >= highest_frequency:
                if hf == highest_frequency:
                    #print(f"Got a tie here {mfw}, {hf}")
                    nr_of_ties+=1
                    most_frequent_words.append(mfw)
                else:
                    highest_frequency = hf #there is a new highest frequency
                    most_frequent_words.clear()
                    most_frequent_words.append(mfw)
                    nr_of_ties=0
        #if len(most_frequent_word) > 0: # do not include weird entry '' with a high frequency
        print(f"Most frequent word(s): {most_frequent_words} with {nr_of_ties+1} ties ")
        if nr_of_ties > 0:
            # IF there is a tie, append all words in alphabetical order
            most_frequent_words.sort()
            for word in most_frequent_words:
                top_n_list.append((word, highest_frequency))
        else:
            top_n_list.append((most_frequent_words[0], highest_frequency))
        for word in most_frequent_words:
            del play_dict[word]
    print("Printing the top_list: ", top_n_list)
    return top_n_list


def cute_print(top_list):
    print(f"Top {len(top_list)} most frequent words:")
    for top_entry in top_list:
        print(f"{top_entry[0]}: {top_entry[1]}")


def main():
    # Define the amount of TOP entries you want to see
    TOP_N = 50

    # The text needs to be cleaned first. E.g. new line characters need to be removed,
    # but also any ',' - ';' - ':' - '?' - '!' or '.'
    # Analyzing the text, there were a lot of unusual characters like [-
    cleaned_text = clean_text(PLAY)
    # print(cleaned_text)

    # derive a list of words from the cleaned text PLAY
    words_from_play = get_words(cleaned_text)

    # create an unordered dictionary with words and their frequency within the text
    the_play_dictionary = words_frequency(words_from_play)

    # order the top 'n' frequencies.
    top_n = top_n_words(the_play_dictionary, TOP_N)

    # print the results cute
    cute_print(top_n)

    # Interesting outcome: Romeo and Juliet, seems more about Romeo than Juliet :-)
    # Romeo: 296
    # Juliet: 178


if __name__ == "__main__":
    main()