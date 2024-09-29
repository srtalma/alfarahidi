import re
import pickle  # or 'import dill as pickle' for better handling of functions across environments
import streamlit as st

# Define the functions
def apply_shadda_rule(word):
    return re.sub(r'(\w)(ّ)(\w?)', r'\1ْ\1\3', word)

def apply_tanween_rule(word):
    word = re.sub(r'([\u0621-\u064A])ً', r'\1an', word)
    word = re.sub(r'([\u0621-\u064A])ٌ', r'\1un', word)
    word = re.sub(r'([\u0621-\u064A])ٍ', r'\1in', word)
    return word

def apply_definite_article_rule(word, position):
    solar_letters = "تثدذرزسشصضطظلن"
    if word.startswith("ال"):
        if position == 'start':
            if word[2] in solar_letters:
                word = f"{word[2]}ّ{word[3:]}"
        else:
            word = f"{word[1:]}"
    return word

def apply_end_of_hemistich_rule(word):
    last_char = word[-1]
    if last_char == 'َ':
        return word + 'a'
    elif last_char == 'ُ':
        return word + 'u'
    elif last_char == 'ِ':
        return word + 'i'
    return word

def remove_initial_hamza_if_preceded(word, preceding_word):
    if preceding_word and re.search(r'[^\s]', preceding_word[-1]):
        if word.startswith('ا'):
            return word[1:]
    return word

def apply_double_consonant_rule(word, preceding_word):
    if preceding_word and preceding_word[-1] in 'ْ':
        return word[1:] if word[0] in 'ْ' else word
    return word

def arabic_to_cv_pattern(word):
    vowels = 'ًٌٍَُِ'
    consonants = 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'

    pattern = ""
    for char in word:
        if char in consonants:
            pattern += 'C'
        elif char in vowels:
            pattern += 'V'
        elif char == 'ّ':
            pattern += ''
        elif char == 'ْ':
            pattern += 'C'
        else:
            pattern += ''
    return pattern

def convert_to_phonetic_and_pattern(text):
    words = text.split()
    phonetic_words = []
    patterns = []

    for i, word in enumerate(words):
        position = 'middle'
        if i == 0:
            position = 'start'
        elif i == len(words) - 1:
            position = 'end'

        word = apply_shadda_rule(word)
        word = apply_tanween_rule(word)
        word = apply_definite_article_rule(word, position)

        if position == 'end':
            word = apply_end_of_hemistich_rule(word)

        if i > 0:
            word = remove_initial_hamza_if_preceded(word, words[i - 1])
            word = apply_double_consonant_rule(word, words[i - 1])

        pattern = arabic_to_cv_pattern(word)
        phonetic_words.append(word)
        patterns.append(pattern)

    return ' '.join(phonetic_words), ' '.join(patterns)

# Save the model (functions) to a pickle file
with open('arabic_text_processing.pkl', 'wb') as f:
    pickle.dump(convert_to_phonetic_and_pattern, f)

# Load the model (function)
with open('arabic_text_processing.pkl', 'rb') as f:
    convert_to_phonetic_and_pattern = pickle.load(f)

# Streamlit App Code
st.title('Arabic Phonetic Converter and CV Pattern Generator')

# Display Al-Farahidi image
st.image("alfarahidi.jpg.webp", caption="Al-Farahidi - Father of Arabic Prosody", use_column_width=True)

st.write("""
### أدخل النص العربي:
تقوم هذه الأداة بتطبيق القواعد اللغوية لتحويل النص العربي إلى كتابة صوتية وأنماط CV.
""")

# Text input field
text = st.text_area("Arabic Text Input", "")

# Button for conversion
if st.button('Convert'):
    if text:
        phonetic_output, pattern_output = convert_to_phonetic_and_pattern(text)
        st.write("### Phonetic Writing:")
        st.write(phonetic_output)
        st.write("### CV Pattern:")
        st.write(pattern_output)
    else:
        st.error("يرجى إدخال نص للتحويل.")
