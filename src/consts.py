
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
        ('coronavirus', 'en'), ('pandemic', 'en'), ('virus', 'en'), ('lockdown', 'en'), ('quarantine', 'en'),
        ('deaths', 'en'), ('masks', 'en'), ('cases', 'en'), ('distancing', 'en'), ('China', 'en'),
    ],
    'Brazil': [
        ('quarentena', 'pt'), ('Babu', 'pt'), ('live', 'pt'), ('Manu', 'pt'), ('Thelma', 'pt'),
        ('pandemia', 'pt'), ('Rafa', 'pt'), ('coronavírus', 'pt'), ('vírus', 'pt'), ('Gizelly', 'pt'),
    ],
    'India': [
        ('यरस', 'hi'), ('तबल', 'hi'), ('मरकज', 'hi'), ('Asharamji', 'hi'), ('तरजन', 'hi'),
        ('Lockdown', 'hi'), ('Corona', 'hi'), ('शट', 'hi'), ('PPE', 'hi'), ('टहन', 'hi'),
    ],
    'Russia': [
        ('коронавируса', 'ru'), ('коронавирусом', 'ru'), ('карантина', 'ru'), ('самоизоляции', 'ru'), ('карантин', 'ru'),
        ('коронавирус', 'ru'), ('пандемии', 'ru'), ('карантине', 'ru'), ('маски', 'ru'), ('эпидемии', 'ru'),
    ],
    'Mexico': [
        ('cuarentena', 'es'), ('pandemia', 'es'), ('coronavirus', 'es'), ('virus', 'es'), ('confinamiento', 'es'),
        ('mascarillas', 'es'), ('casos', 'es'), ('salud', 'es'), ('sanitaria', 'es'), ('fallecidos', 'es'),
    ],
    'Iran': [
        ('کرونا', 'fa'), ('ویروس', 'fa'), ('قرنطینه', 'fa'), ('ماسک', 'fa'), ('چین', 'fa'),
        ('شیوع', 'fa'), ('بهداشت', 'fa'), ('مبتلا', 'fa'), ('ساعات', 'fa'), ('بیماری', 'fa'),
    ],
    'Korea, South': [
        ('코로나', 'ko'), ('한승우', 'ko'), ('승우', 'ko'), ('n번방', 'ko'), ('코로나19', 'ko'),
        ('마스크', 'ko'), ('스위치', 'ko'), ('해찬', 'ko'), ('#스밍', 'ko'), ('N번방', 'ko'),
    ],
    'Italy': [
        ('Coronavirus', 'it'), ('quarantena', 'it'), ('virus', 'it'), ('MES', 'it'), ('mascherine', 'it'),
        ('Lombardia', 'it'), ('pandemia', 'it'), ('Conte', 'it'), ('contagi', 'it'), ('mascherina', 'it'),
    ],
    'France': [
        ('confinement', 'fr'), ('masques', 'fr'), ('Coronavirus', 'fr'), ('virus', 'fr'), ('masque', 'fr'),
        ('pandémie', 'fr'), ('sanitaire', 'fr'), ('crise', 'fr'), ('tests', 'fr'), ('soignants', 'fr'),
    ],
    'Germany': [
        ('Corona', 'de'), ('Masken', 'de'), ('Virus', 'de'), ('GT', 'de'), ('Krise', 'de'),
        ('Coronavirus', 'de'), ('Pandemie', 'de'), ('Maske', 'de'), ('Abstand', 'de'), ('bgt', 'de'),
    ],
    'Sweden': [
        ('Tegnell', 'sv'), ('Corona', 'sv'), ('Ak', 'sv'), ('FHM', 'sv'), ('ak', 'sv'),
        ('makasii', 'sv'), ('tidur', 'sv'), ('smittade', 'sv'), ('viruset', 'sv'), ('bgt', 'sv'),
    ],
    'Turkey': [
        ('maske', 'tr'), ('virüs', 'tr'), ('çıkma', 'tr'), ('sağlık', 'tr'), ('koronavirüs', 'tr'),
        ('vaka', 'tr'), ('Sağlık', 'tr'), ('evde', 'tr'), ('yardım', 'tr'), ('yasağı', 'tr'),
    ],
}
