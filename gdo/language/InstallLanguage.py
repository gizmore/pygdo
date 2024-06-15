from gdo.language.GDO_Language import GDO_Language


class InstallLanguage:
    LANGUAGES = [
        ['English', 'English', 'eng', 'en'],
        ['German', 'Deutsch', 'ger', 'de'],
        ['French', 'Française', 'fre', 'fr'],
        ['Bulgarian', 'български език', 'bul', 'bg'],
        ['Brazil', 'Brazil', 'bra', 'br'],
        ['Spanish', 'español', 'spa', 'es'],
        ['Chinese', '汉语 / 漢語', 'chi', 'zh'],
        ['Croatian', 'hrvatski', 'cro', 'hr'],
        ['Albanian', 'Shqip', 'alb', 'sq'],
        ['Arabic', 'العربية', 'ara', 'ar'],
        # ['Amazigh', '', 'ama', ''],
        ['Catalan', 'català', 'cat', 'ca'],
        ['Armenian', 'Հայերեն', 'arm', 'hy'],
        ['Azerbaijani', 'Azərbaycan / Азәрбајҹан / آذربایجان دیلی', 'aze', 'az'],
        ['Bengali', 'বাংলা', 'ben', 'bn'],
        ['Dutch', 'Nederlands', 'dut', 'nl'],
        ['Bosnian', 'bosanski/босански', 'bos', 'bs'],
        ['Serbian', 'Српски / Srpski', 'ser', 'sr'],
        ['Portuguese', 'português', 'por', 'pt'],
        ['Greek', 'Ελληνικά / Ellīniká', 'gre', 'el'],
        ['Turkish', 'Türkçe', 'tur', 'tr'],
        ['Czech', 'Čeština', 'cze', 'cs'],
        ['Danish', 'dansk', 'dan', 'da'],
        ['Finnish', 'suomi', 'fin', 'fi'],
        ['Swedish', 'svenska', 'swe', 'sv'],
        ['Hungarian', 'magyar', 'hun', 'hu'],
        ['Icelandic', 'Íslenska', 'ice', 'is'],
        ['Hindi', 'हिन्दी / हिंदी', 'hin', 'hi'],
        ['Persian', 'فارسی', 'per', 'fa'],
        ['Kurdish', 'Kurdî / کوردی', 'kur', 'ku'],
        ['Irish', 'Gaeilge', 'iri', 'ga'],
        ['Hebrew', 'עִבְרִית / \'Ivrit', 'heb', 'he'],
        ['Italian', 'Italiano', 'ita', 'it'],
        ['Japanese', '日本語 / Nihongo', 'jap', 'ja'],
        ['Korean', '한국어 / 조선말', 'kor', 'ko'],
        ['Latvian', 'latviešu valoda', 'lat', 'lv'],
        ['Lithuanian', 'Lietuvių kalba', 'lit', 'lt'],
        ['Luxembourgish', 'Lëtzebuergesch', 'lux', 'lb'],
        ['Macedonian', 'Македонски јазик / Makedonski jazik', 'mac', 'mk'],
        ['Malay', 'Bahasa Melayu / بهاس ملايو', 'mal', 'ms'],
        ['Dhivehi', 'Dhivehi / Mahl', 'dhi', 'dv'],
        # ['Montenegrin', 'Црногорски / Crnogorski', 'mon', ''],
        ['Maori', 'Māori', 'mao', 'mi'],
        ['Norwegian', 'norsk', 'nor', 'no'],
        ['Filipino', 'Filipino', 'fil', 'tl'],
        ['Polish', 'język polski', 'pol', 'pl'],
        ['Romanian', 'română / limba română', 'rom', 'ro'],
        ['Russian', 'Русский язык', 'rus', 'ru'],
        ['Slovak', 'slovenčina', 'slo', 'sk'],
        # ['Mandarin', '官話 / Guānhuà', 'man', 'zh'],
        ['Tamil', 'தமிழ', 'tam', 'ta'],
        ['Slovene', 'slovenščina', 'slv', 'sl'],
        ['Zulu', 'isiZulu', 'zul', 'zu'],
        ['Xhosa', 'isiXhosa', 'xho', 'xh'],
        ['Afrikaans', 'Afrikaans', 'afr', 'af'],
        # ['Northern Sotho', 'Sesotho sa Leboa', 'nso', '--'],
        ['Tswana', 'Setswana / Sitswana', 'tsw', 'tn'],
        ['Sotho', 'Sesotho', 'sot', 'st'],
        ['Tsonga', 'Tsonga', 'tso', 'ts'],
        ['Thai', 'ภาษาไทย / phasa thai', 'tha', 'th'],
        ['Ukrainian', 'українська мова', 'ukr', 'uk'],
        ['Vietnamese', 'Tiếng Việt', 'vie', 'vi'],
        ['Pashto', 'پښت', 'pas', 'ps'],
        ['Samoan', 'gagana Sāmoa', 'sam', 'sm'],
        # ['Bajan', 'Barbadian Creole', 'baj', '--'],
        ['Belarusian', 'беларуская мова', 'bel', 'be'],
        # ['Dzongkha', '', 'dzo', 'dz'],
        # ['Quechua', '', 'que', ''],
        # ['Aymara', '', 'aym', ''],
        # ['Setswana', '', 'set', ''],
        # ['Bruneian', '', 'bru', ''],
        # ['Indigenous', '', 'ind', ''],
        # ['Kirundi', '', 'kir', ''],
        # ['Swahili', '', 'swa', ''],
        # ['Khmer', '', 'khm', ''],
        # ['Sango', '', 'san', ''],
        # ['Lingala', '', 'lin', ''],
        # ['Kongo/Kituba', '', 'kon', ''],
        # ['Tshiluba', '', 'tsh', ''],
        # ['Afar', '', 'afa', ''],
        # ['Somali', '', 'som', ''],
        # ['Fang', '', 'fan', ''],
        # ['Bube', '', 'bub', ''],
        # ['Annobonese', '', 'ann', ''],
        # ['Tigrinya', '', 'tig', ''],
        # ['Estonian', 'Eesti', 'est', 'et'],
        # ['Amharic', '', 'amh', ''],
        # ['Faroese', '', 'far', ''],
        # ['Bau Fijian', '', 'bau', ''],
        # ['Hindustani', '', 'hit', ''],
        # ['Tahitian', '', 'tah', ''],
        # ['Georgian', '', 'geo', ''],
        # ['Greenlandic', '', 'grl', ''],
        # ['Chamorro', '', 'cha', ''],
        # ['Crioulo', '', 'cri', ''],
        # ['Haitian Creole', '', 'hai', ''],
        # ['Indonesian', '', 'inn', ''],
        # ['Kazakh', '', 'kaz', ''],
        # ['Gilbertese', '', 'gil', ''],
        # ['Kyrgyz', '', 'kyr', ''],
        # ['Lao', '', 'lao', ''],
        # ['Southern Sotho', '', 'sso', ''],
        # ['Malagasy', '', 'mag', ''],
        # ['Chichewa', '', 'chw', ''],
        # ['Maltese', '', 'mat', ''],
        # ['Marshallese', '', 'mar', ''],
        # ['Moldovan', '', 'mol', ''],
        # ['Gagauz', '', 'gag', ''],
        # ['Monegasque', '', 'moq', ''],
        # ['Mongolian', '', 'mgl', ''],
        # ['Burmese', '', 'bur', ''],
        # ['Oshiwambo', '', 'osh', ''],
        # ['Nauruan', '', 'nau', ''],
        # ['Nepal', '', 'nep', ''],
        # ['Papiamento', '', 'pap', ''],
        # ['Niuean', '', 'niu', ''],
        # ['Norfuk', '', 'nfk', ''],
        # ['Carolinian', '', 'car', ''],
        # ['Urdu', 'اردو', 'urd', 'ur'],
        # ['Palauan', '', 'pal', ''],
        # ['Tok Pisin', '', 'tok', ''],
        # ['Hiri Motu', '', 'hir', ''],
        # ['Guarani', '', 'gua', ''],
        # ['Pitkern', '', 'pit', ''],
        # ['Kinyarwanda', '', 'kin', ''],
        # ['Antillean Creole', '', 'ant', ''],
        # ['Wolof', '', 'wol', ''],
        # ['Sinhala', '', 'sin', ''],
        # ['Sranan Tongo', '', 'sra', ''],
        # ['Swati', '', 'swt', ''],
        # ['Syrian', '', 'syr', ''],
        # ['Tajik', '', 'taj', ''],
        # ['Tetum', '', 'tet', ''],
        # ['Tokelauan', '', 'tol', ''],
        # ['Tongan', '', 'ton', ''],
        # ['Turkmen', '', 'tkm', ''],
        # ['Uzbek', '', 'uzb', ''],
        # ['Dari', '', 'dar', ''],
        # ['Tuvaluan', '', 'tuv', ''],
        # ['Bislama', '', 'bis', ''],
        # ['Uvean', '', 'uve', ''],
        # ['Futunan', '', 'fut', ''],
        # ['Shona', '', 'sho', ''],
        # ['Sindebele', '', 'sid', ''],
        # ['Taiwanese', '', 'tai', ''],
        # ['Manx', '', 'max', ''],
        ['Fanmglish', 'Famster', 'fam', 'xf'],
        ['Bot', 'BotJSON', 'bot', 'xb'],
        ['Ibdes', 'RFCBotJSON', 'ibd', 'xi'],
        ['Test Japanese', 'Test Japanese', 'ori', 'xo'],
    ]

    @classmethod
    def now(cls):
        if GDO_Language.table().count_where() == 0:
            cls.install_languages()

    @classmethod
    def install_languages(cls):
        bulk = []
        headers = GDO_Language.table().columns_only('lang_english', 'lang_native', 'lang_iso')
        for data in cls.LANGUAGES:
            bulk_data = [data[0], data[1], data[3]]
            bulk.append(bulk_data)
        GDO_Language.table().bulk_insert(headers, bulk)
