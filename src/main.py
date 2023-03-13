#encoding=utf-8
import os
import jieba
import numpy as np
import pandas as pd
import jieba.posseg as pseg

exclude_items = ('ad', 'c', 'm', 'n', 'r', 'u', 'p', 'xc', 'd', 'p')
seeds = []
words = [{}, {}]


def is_Chinese(ch):
    if '\u4e00' <= ch <= '\u9fff':
        return True
    return False


def update(result, index):
    for r in result:
        if len(r.word) > 1:
            value = words[index].get(r.word)
            if value is None:
                value = 0
            words[index].update({r.word: value + 1})


def check(result, mark):
    end = len(result) - 1
    has = True
    rm = set()  # index of seeds in result
    for r in range(0, end):
        while r <= end and not is_Chinese(result[r].word):
            result.pop(r)
            end -= 1

        if r > end:
            if has:
                for i in (sorted(rm, reverse=True)):
                    result.pop(i)  # remove seeds from result
                update(result, mark)
            return

        for seed in seeds[mark]:
            if result[r].word.find(
                    seed) == -1 and result[r].flag not in exclude_items:
                continue
            else:  # sentence contains seeds, remove seeds
                has = True
                rm.add(r)  # save index


def cut(value):
    r = pseg.lcut(value[1])
    check(r, value[0])


def preprocess():
    jieba.suggest_freq(('不新鲜', '特别', '不能吃', '差评'), True)


if __name__ == '__main__':
    print('Running...')
    root = '/Users/aaroncomo/coding/python/projects/sentiment_analysis'
    try:
        os.remove(os.path.join(root, 'output.txt'))
    except:
        pass

    with open(os.path.join(root, 'data', 'seeds.txt'), mode='r',
              encoding='utf-8') as fi:
        seeds.append(fi.readline().replace('\n', '').split(' '))
        seeds.append(fi.readline().split(' '))
        fi.close()

    dataset = np.array(pd.read_csv(os.path.join(root, 'data', '外卖评论.csv')))
    preprocess()
    for d in dataset:
        cut(d)

    words[0] = sorted(words[0].items(), key=lambda x: x[1], reverse=True)
    words[1] = sorted(words[1].items(), key=lambda x: x[1], reverse=True)

    with open(os.path.join(root, 'output.txt'), 'w') as fi:
        fi.write('好评中最常出现的词: \n')
        for i in range(0, 50):
            fi.write('{}:\t{}\t出现了{}次\n'.format(i + 1, words[1][i][0],
                                                words[1][i][1]))
        fi.write('\n差评中最常出现的词: \n')
        for i in range(0, 50):
            fi.write('{}:\t{}\t出现了{}次\n'.format(i + 1, words[0][i][0],
                                                words[0][i][1]))
    print('Done. See \'output.txt\' for more details.')
