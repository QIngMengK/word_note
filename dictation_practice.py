import random

# 从单词列表中选择 5 个单词进行听写
def start_dictation(words):
    selected_words = random.sample(words, 5)  # 随机选取 5 个单词
    dictation_data = {word['word']: word['translation'] for word in selected_words}
    return dictation_data

