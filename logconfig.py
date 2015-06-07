# -*- coding: utf-8 -*-# -*- mode: python -*-

logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(name)s %(levelname)s: %(message)s',
            'formatter': 'default',
            }
        },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            },
        'Default': {
            'level': 'INFO',
            'class' : 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'logs/Default.log',
        },
        'Evaluator': {
            'level': 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'logs/Evaluator.log',
        },
        'WipeThread': {
            'level': 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'logs/WipeThread.log',
        },
        'Grabber': {
            'level': 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'logs/Grabber.log',
        },
        'UniWipe': {
            'level': 'DEBUG',
            'class' : 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'logs/ThreadWipe.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['Default'],
            'level': 'DEBUG',
        },
        'EvaluatorProxy': { 'handlers': ['Evaluator'], },
        'WipeThread': { 'handlers': ['WipeThread'], },
        'Grabber': { 'handlers': ['Grabber'], },
        'UniWipe': { 'handlers': ['UniWipe'], },
    },
}
