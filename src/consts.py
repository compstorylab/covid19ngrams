
import matplotlib.font_manager as fm
fm._rebuild()
noto = [f.name for f in fm.fontManager.ttflist if 'Noto Sans' in f.name]

fonts = {
    'Default': fm.FontProperties(family=["sans-serif"]),
    'Korean': fm.FontProperties(family=["Noto Sans CJK KR", "Noto Sans CJK", "sans-serif"]),
    'Tamil': fm.FontProperties(family=["Noto Sans Tamil", "sans-serif"]),
}

at_color = 'k'
ot_color = 'C0'
rt_color = 'C1'
tags = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split(' ')

countries = [
    'United States', 'Brazil', 'India',
    'Russia', 'Italy', 'Mexico',
    'Iran', 'France', 'Germany',
    'Saudi Arabia', 'Turkey', 'Indonesia'
]


contagiograms = {
    'virus_12': [
        ('virus', 'en'), ('virus', 'es'), ('vírus', 'pt'), ('فيروس', 'ar'),
        ('바이러스', 'ko'), ('virus', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
        ('Virus', 'de'), ('virus', 'it'), ('вирус', 'ru'), ('virus', 'tl'),
    ],
    'virus_24': [
        ('virus', 'hi'), ('ویروس', 'fa'), ('وائرس', 'ur'), ('wirus', 'pl'),
        ('virus', 'ca'), ('virus', 'nl'), ('virus', 'ta'), ('ιός', 'el'),
        ('virus', 'sv'), ('вирус', 'sr'), ('virus', 'fi'), ('вірус', 'uk'),
    ],
    'samples_1grams_12': [
        ('coronavirus', 'en'), ('cuarentena', 'es'), ('corona', 'pt'), ('كورونا', 'ar'),
        ('바이러스', 'ko'), ('quarantaine', 'fr'), ('virus', 'id'), ('virüs', 'tr'),
        ('Quarantäne', 'de'), ('quarantena', 'it'), ('карантин', 'ru'), ('virus', 'tl'),
    ],
    'samples_1grams_24': [
        ('virus', 'hi'), ('قرنطینه', 'fa'), ('مرضی', 'ur'), ('testów', 'pl'),
        ('confinament', 'ca'), ('virus', 'nl'), ('ரஜ', 'ta'), ('σύνορα', 'el'),
        ('Italien', 'sv'), ('mere', 'sr'), ('manaa', 'fi'), ('BARK', 'uk'),
    ],
    'samples_2grams': [
        ('social distancing', 'en'), ('public health', 'en'), ('the lockdown', 'en'), ('health workers', 'en'),
        ('small businesses', 'en'), ('stimulus check', 'en'), ('during quarantine', 'en'), ('Anthony Fauci', 'en'),
        ('laid off', 'en'), ('panic buying', 'en'), ('stay home', 'en'), ('cultural reset', 'en'),
    ],
}

words_by_country = {
    'United States': [
        ('virus', 'en'), ('coronavirus', 'en'), ('COVID-19', 'en'), ('pandemic', 'en'), ('#COVID19', 'en')
    ],
    'Brazil': [
        ('vírus', 'pt'), ('corona', 'pt'), ('quarentena', 'pt'), ('coronavírus', 'pt'), ('#COVID19', 'pt')
    ],
    'India': [
        ('virus', 'hi'), ('मरकज', 'hi'), ('तबल', 'hi'), ('#lockdown', 'hi'), ('#COVID19', 'hi')
    ],
    'Russia': [
        ('вирус', 'ru'), ('карантин', 'ru'), ('коронавируса', 'ru'), ('самоизоляции', 'ru'), ('#COVID19', 'ru')
    ],
    'Italy': [
        ('virus', 'it'), ('quarantena', 'it'), ('Coronavirus', 'it'), ('pandemia', 'it'), ('#COVID19', 'it')
    ],
    'Mexico': [
        ('virus', 'es'), ('coronavirus', 'es'), ('cuarentena', 'es'), ('pandemia', 'es'), ('#COVID19', 'es')
    ],
    'Iran': [
        ('ویروس', 'fa'), ('قرنطینه', 'fa'), ('کرونا', 'fa'), ('#كرونا', 'fa'), ('#کروناویروس', 'fa')
    ],
    'France': [
        ('virus', 'fr'), ('quarantaine', 'fr'), ('confinement', 'fr'), ('Coronavirus', 'fr'), ('#COVID19', 'fr')
    ],
    'Germany': [
        ('Virus', 'de'), ('Corona', 'de'), ('Coronavirus', 'de'), ('Quarantäne', 'de'), ('#COVID19', 'de')
    ],
    'Saudi Arabia': [
        ('فيروس', 'ar'), ('كورونا', 'ar'), ('الوباء', 'ar'), ('#فيروس_كورونا', 'ar'), ('#كورونا', 'ar')
    ],
    'Turkey': [
        ('virüs', 'tr'), ('Koronavirüs', 'tr'), ('maske', 'tr'), ('korona', 'tr'), ('#COVID19', 'tr')
    ],
    'Indonesia': [
        ('virus', 'id'), ('corona', 'id'), ('pandemi', 'id'), ('masker', 'id'), ('#COVID19', 'id')
    ],
}
