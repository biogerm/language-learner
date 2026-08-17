import sqlite3
import random

conn = sqlite3.connect('course/sfid/phase3/output/b1_vocab.db')
cursor = conn.cursor()

def get_sample(word_type, limit=20):
    cursor.execute(f"SELECT * FROM b1_vocabulary WHERE word_type = '{word_type}'")
    rows = cursor.fetchall()
    return random.sample(rows, min(len(rows), limit))

verbs = get_sample('Verb')
nouns = get_sample('Noun')
adjs = get_sample('Adjective')

conn.close()

with open('db_sample_data.md', 'w') as f:
    f.write("# 数据库抽样展示 (20个动词、名词、形容词)\n\n")
    
    # Verbs
    f.write("## 1. 动词 (Verbs)\n")
    f.write("| 单词 | 翻译 | 原型/祈使 | 现在时 | 过去时 | 动名词 (Supinum) | 过去分词 | 例句 | 音频 |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for r in verbs:
        # Schema: word(0), word_type(1), noun_gender(2), is_regular(3), imp(4), pres(5), pret(6), sup(7), perf(8), adj_en(9), ett(10), plur(11), komp(12), sup(13), trans(14), context(15), audio(16), source(17)
        word = r[0]
        trans = r[14]
        imp = r[4] or '-'
        pres = r[5] or '-'
        pret = r[6] or '-'
        sup = r[7] or '-'
        perf = r[8] or '-'
        ctx = r[15]
        audio = r[16] or 'NULL'
        f.write(f"| {word} | {trans} | {imp} | {pres} | {pret} | {sup} | {perf} | {ctx} | {audio} |\n")
        
    # Nouns
    f.write("\n## 2. 名词 (Nouns)\n")
    f.write("| 单词 | 词性 | 翻译 | 例句 | 音频 |\n")
    f.write("|---|---|---|---|---|\n")
    for r in nouns:
        word = r[0]
        gender = r[2] or '-'
        trans = r[14]
        ctx = r[15]
        audio = r[16] or 'NULL'
        f.write(f"| {word} | {gender} | {trans} | {ctx} | {audio} |\n")
        
    # Adjectives
    f.write("\n## 3. 形容词 (Adjectives)\n")
    f.write("| 单词 | 翻译 | en形式 | ett形式 | 复数形式 | 比较级 | 最高级 | 例句 | 音频 |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for r in adjs:
        word = r[0]
        trans = r[14]
        adj_en = r[9] or '-'
        ett = r[10] or '-'
        plur = r[11] or '-'
        komp = r[12] or '-'
        sup = r[13] or '-'
        ctx = r[15]
        audio = r[16] or 'NULL'
        f.write(f"| {word} | {trans} | {adj_en} | {ett} | {plur} | {komp} | {sup} | {ctx} | {audio} |\n")

print("Generated full detailed samples.")
