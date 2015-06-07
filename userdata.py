from sup import randstr
import wordsgen

def short_wordsgen():
    userdata = {'login': randstr(6, 10),
                'passwd': randstr(6, 10),
                'name': ' '.join((wordsgen.gen_word().capitalize(),
                                  wordsgen.gen_word().capitalize(),
                                  )),
                0: {}}
    return userdata
