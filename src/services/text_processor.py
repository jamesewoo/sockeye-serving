import html
import os
import subprocess
from html.entities import html5, name2codepoint

import regex as re
from subword_nmt.apply_bpe import BPE


def run_subprocess(text, args):
    """
    Runs a subprocess that process text
    :param text: input text
    :param args: command line arguments
    :return: processed text
    """
    popen = subprocess.run(args, input=text, encoding='utf-8', stdout=subprocess.PIPE)
    return popen.stdout.strip()


class TextProcessor:
    def __init__(self):
        symbols = ''
        symbol_set = set({})

        for k in name2codepoint.keys():
            symbol_set.add(k)

        for k in html5.keys():
            symbol_set.add(k.strip(';'))

        for s in symbol_set:
            symbols += '|' + s

        symbols = symbols.strip('|')

        self.single = re.compile('&[ ]?(' + symbols + ')[ ]?;', re.IGNORECASE)
        self.double = re.compile('&[ ]?amp[ ]?;[ ]?(' + symbols + ')[ ]?;', re.IGNORECASE)

        self.singleNum = re.compile('&[ ]?#[ ]?([0-9]+)[ ]?;', re.IGNORECASE)
        self.doubleNum = re.compile('&[ ]?amp[ ]?;[ ]?#[ ]?([0-9]+)[ ]?;', re.IGNORECASE)

        self.singleXNum = re.compile('&[ ]?#[ ]?x[ ]?([a-f0-9]+)[ ]?;', re.IGNORECASE)
        self.doubleXNum = re.compile('&[ ]?amp[ ]?;[ ]?#[ ]?x[ ]?([a-f0-9]+)[ ]?;', re.IGNORECASE)

        self.nbsp = re.compile('(&[ ]?x?[ ]?n[]?b[ ]?([a-z][ ]?){0,6}[ ]?;)|(&[ ]?o[ ]?s[ ]?p[ ]?;)', re.IGNORECASE)

        self.shy = re.compile('[ ]?&[ ]?s[ ]?h[ ]?y[ ]?;[ ]?', re.IGNORECASE)

        self.bpe = None

    def unescape(self, line):
        # put html-escaped (or double escaped) codes back into canonical format
        line = re.sub(self.double, r'&\1;', line)
        line = re.sub(self.doubleNum, r'&#\1;', line)
        line = re.sub(self.doubleXNum, r'&#x\1;', line)
        line = re.sub(self.single, r'&\1;', line)
        line = re.sub(self.singleNum, r'&#\1;', line)
        line = re.sub(self.singleXNum, r'&#x\1;', line)

        # get rid of this tag
        # alphabetic characters -- need only get rid of space around their canonical escaped forms
        line = re.sub(self.shy, '', line)

        # unescape
        line = html.unescape(line)

        # clean up weird errors in the escaping of the non-breaking space
        line = re.sub(self.nbsp, ' ', line)
        return line

    def run(self, text):
        return self.unescape(text)


class BpeEncoder(TextProcessor):
    def __init__(self, bpe_code_file):
        super().__init__()

        with open(bpe_code_file, mode='r', encoding='utf-8') as f:
            self.bpe = BPE(f)

    def run(self, text):
        return self.bpe.process_line(text).strip()


class JoshuaPreprocessor(TextProcessor):
    def __init__(self, scripts_path, lang):
        super().__init__()

        self.lang = lang
        self.normalizer = os.path.join(scripts_path, 'normalize.pl')
        self.tokenizer = os.path.join(scripts_path, 'tokenizer.perl')
        self.cleaner = os.path.join(scripts_path, 'remove-non-printing-char.perl')

        for f in [self.normalizer, self.tokenizer, self.cleaner]:
            os.chmod(f, 0o755)

    def run(self, text):
        text = self.unescape(text)
        return run_subprocess(text,
                              [self.normalizer, self.lang, '|', self.cleaner, '|', self.tokenizer, '-l', self.lang,
                               '-no-escape', '-q'])


class ChineseCharPreprocessor(JoshuaPreprocessor):
    def __init__(self, scripts_path):
        super().__init__(scripts_path, 'zh')

        self.pattern = re.compile(
            '([\p{IsHan}\p{InCJK_Symbols_and_Punctuation}\p{InCJK_Radicals_Supplement}\p{InCJK_Compatibility}])',
            re.UNICODE)

    def run(self, text):
        text = self.unescape(text)

        # normalize and remove non-printing characters
        text = run_subprocess(text, [self.normalizer, self.lang, '|', self.cleaner])

        # tokenize by separating all ZH characters with a space
        text = self.pattern.sub(r' \1 ', text).strip()

        # tokenize other characters using Moses
        return run_subprocess(text, [self.tokenizer, '-l', self.lang, '-no-escape', '-q'])


class Detokenizer(TextProcessor):
    def __init__(self, scripts_path):
        super().__init__()

        self.de_bpe = re.compile('@@( |$)', re.IGNORECASE)
        self.de_tok = os.path.join(scripts_path, 'detokenize.pl')

        os.chmod(self.de_tok, 0o755)

    def run(self, text):
        text = re.sub(self.de_bpe, '', text.translation.strip())
        return run_subprocess(text, [self.de_tok, '-l', 'en'])
