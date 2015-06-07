#!/bin/env python
# -*- coding: utf-8 -*-

import random

PREFIXES = ["в-", "во-", "взо-", "вы-", "до-", "за-", "изо-",
            "ко-", "на-", "над-", "надо-", "не-", "недо-", "о-",
            "об-", "обо-", "от-", "ото-", "па-", "по-", "под-", "подо-",
            "пра-", "пред-", "предо-", "про-", "разо-", "с-", "со-", "су-",
            "у-", "без-", "бес-", "вз-", "вс-", "воз-", "вос-", "из-",
            "ис-", "низ-", "нис-", "раз-", "рас-", "роз-", "рос-", "через-",
            "черес-", "пре-", "при-"]

ROOTS = [ "лаг-", "рас-", "каст-", "кит-", "суп-", "дом-",
          "кот-", "бум-", "авто-", "дуб-", "код-",
          "секс-", "пис-", "рог-", "суп-", "люб-", "нах-",
          "древ-", "стол-", "тумб-", "ламп-", "заб-",
          "стен-", "лист-", "кол-", "урож-", "пул-", "ствол-",
          "текст-", "брауз-", "евген-", "плюх-"]

SUFFIXES = [ "ан", "ян-", "анин", "янин", "ач", "ени", "ет-", "еств-", "ств-",
             "есть", "ец", "изм", "изн-", "ик" "ник", "ин", "ист", "итель",
             "тель", "их", "иц-", "ниц-", "к-", "л-", "лк", "льник", "льщик",
             "льщиц-", "ни", "от-", "ость", "ун", "чик", "щик", "чиц-", "ать", "ять"]

ENDS = [ "о", "а", "ы", "ец", "е", "ый", "ий", "ие", "ой", "ай", "ище" ]

WORD_PARTS = [
    { "data": PREFIXES, "prob": 0.7 },
    { "data": ROOTS, "prob": 1.0 },
    { "data": SUFFIXES, "prob": 0.6 },
    { "data": ENDS, "prob": 0.75 }]

def gen_word():
    res = ""
    for parts in WORD_PARTS:
        if parts["prob"] < 1.0:
            if random.random() > parts["prob"]:
                continue
        p = random.choice(parts["data"])
        if not p.endswith("-"):
            res += p
            break
        else:
            res += p.strip("-")
    return res

if __name__ == "__main__":
    import sys
    for i in range(random.randint(3, 10)):
        words = []
        for i in range(random.randint(3, 10)):
            words.append(gen_word())
        print("%s."%' '.join((words)))