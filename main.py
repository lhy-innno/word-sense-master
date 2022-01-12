# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template, request
import os
import jieba
from math import log2
import pachong

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html', meanings=[], meaning='')


# 接收表单提交的路由，需要指定methods
@app.route('/index', methods=['POST', 'GET'])
def answer():
    if request.method == 'POST':
        question = request.form
        meanings, meaning = disambiguate(question['词语'], question['句子'])
        return render_template('index.html', meanings=meanings, meaning=meaning)
    else:
        return render_template('index.html', meanings=[], meaning='')


def disambiguate(ci, jv):
    word = ci
    sentence = jv
    if word == 'out':
        exit(0)
    print("请稍等……")
    try:
        url = 'https://baike.baidu.com/item/' + word
        pachong.WebScrape(word, url).run1()

        jieba.add_word(word)
        sent_words = list(jieba.cut(sentence, cut_all=False))

        # 去掉停用词
        stopwords = [word, '我', '你', '它', '他', '她', '了', '是', '的', '啊', '谁',
                     '什么', '都', '很', '个', '之', '人', '在', '上', '下', '左', '右',
                     '。', '，', '、', '！', '？', '（', '）']

        sent_cut = []
        for wor in sent_words:
            if wor not in stopwords:
                sent_cut.append(wor)

        print(sent_cut)

        # 计算其他词的TF-IDF以及频数
        wsd_dict = {}
        dir = os.listdir('.')
        for file in os.listdir('.'):
            if word in file:
                wsd_dict[file.replace('.txt', '')] = read_file(file)

        # 统计每个词语在语料中的词频
        tf_dict = {}
        for meaning, sents in wsd_dict.items():
            tf_dict[meaning] = []
            for wor in sent_cut:
                word_count = 0
                for sent in sents:
                    example = list(jieba.cut(sent, cut_all=False))
                    word_count += example.count(wor)

                if word_count:
                    tf_dict[meaning].append((wor, word_count))

        # 统计每个词语的逆向文件频率
        idf_dict = {}
        for wor in sent_cut:
            document_count = 0
            for meaning, sents in wsd_dict.items():
                for sent in sents:
                    if wor in sent:
                        document_count += 1

            idf_dict[wor] = document_count

        # 输出值
        total_document = 0
        for meaning, sents in wsd_dict.items():
            total_document += len(sents)

        # 计算tf_idf值
        mean_tf_idf = []
        for k, v in tf_dict.items():
            print(k + ':')
            tf_idf_sum = 0
            for item in v:
                wor = item[0]
                tf = item[1]
                tf_idf = item[1] * log2(total_document / (1 + idf_dict[wor]))
                tf_idf_sum += tf_idf
                print('%s, 频数为: %s, TF-IDF值为: %s' % (wor, tf, tf_idf))

            mean_tf_idf.append((k, tf_idf_sum))

        sort_array = sorted(mean_tf_idf, key=lambda x: x[1], reverse=True)
        true_meaning = sort_array[0][0].split('_')[1]
        print('\n经过词义消岐，%s在该句子中的意思为：%s。' % (word, true_meaning))

        delete_files()
        meanings = pachong.meaning
        pachong.meaning = []
        pachong.hrefs = []
        return meanings, '\n经过词义消岐，%s在该句子中的意思为：%s。' % (word, true_meaning)
    except AttributeError:
        print("出错了")


# 读取每个义项的语料
def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = [_.strip() for _ in f.readlines()]
        return lines


def delete_files():
    for foldName, subfolders, filenames in os.walk(
            r'D:\Python\wordSense-master2\wordSense-master'):  # 用os.walk方法取得path路径下的文件夹路径，子文件夹名，所有文件名
        for filename in filenames:  # 遍历列表下的所有文件名
            if filename.endswith('.txt'):  # 当文件名以.txt后缀结尾时
                os.remove(os.path.join(foldName, filename))  # 删除符合条件的文件


if __name__ == '__main__':
    app.run(debug=True)
