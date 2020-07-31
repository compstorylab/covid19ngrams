
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
