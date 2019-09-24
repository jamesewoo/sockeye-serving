import html
import os
import unicodedata
from html.entities import html5, name2codepoint
from typing import List

import regex as re
from subword_nmt.apply_bpe import BPE

from .utils import run_subprocess


class TextProcessor:
    """
    Transforms text as part of either preprocessing or postprocessing
    """

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
        self.double = re.compile(
            '&[ ]?amp[ ]?;[ ]?(' + symbols + ')[ ]?;',
            re.IGNORECASE)

        self.singleNum = re.compile('&[ ]?#[ ]?([0-9]+)[ ]?;', re.IGNORECASE)
        self.doubleNum = re.compile(
            '&[ ]?amp[ ]?;[ ]?#[ ]?([0-9]+)[ ]?;',
            re.IGNORECASE)

        self.singleXNum = re.compile(
            '&[ ]?#[ ]?x[ ]?([a-f0-9]+)[ ]?;', re.IGNORECASE)
        self.doubleXNum = re.compile(
            '&[ ]?amp[ ]?;[ ]?#[ ]?x[ ]?([a-f0-9]+)[ ]?;',
            re.IGNORECASE)

        self.nbsp = re.compile(
            '(&[ ]?x?[ ]?n[]?b[ ]?([a-z][ ]?){0,6}[ ]?;)|(&[ ]?o[ ]?s[ ]?p[ ]?;)',
            re.IGNORECASE)

        self.shy = re.compile('[ ]?&[ ]?s[ ]?h[ ]?y[ ]?;[ ]?', re.IGNORECASE)

        self.bpe = None

    def remove_control_characters(self, s):
        return ''.join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    def unescape(self, line):
        # put html-escaped (or double escaped) codes back into canonical format
        line = re.sub(self.double, r'&\1;', line)
        line = re.sub(self.doubleNum, r'&#\1;', line)
        line = re.sub(self.doubleXNum, r'&#x\1;', line)
        line = re.sub(self.single, r'&\1;', line)
        line = re.sub(self.singleNum, r'&#\1;', line)
        line = re.sub(self.singleXNum, r'&#x\1;', line)

        # get rid of this tag
        # alphabetic characters -- need only get rid of space around their
        # canonical escaped forms
        line = re.sub(self.shy, '', line)

        # unescape
        line = html.unescape(line)

        # clean up weird errors in the escaping of the non-breaking space
        line = re.sub(self.nbsp, ' ', line)
        return line

    def run(self, text):
        text = self.unescape(text)
        return self.remove_control_characters(text)


class BpeEncoder(TextProcessor):
    """
    Returns byte-pair encodings of text
    """

    def __init__(self, bpe_code_file):
        super().__init__()

        with open(bpe_code_file, mode='r', encoding='utf-8') as f:
            self.bpe = BPE(f)

    def run(self, text):
        if not text:
            return ''
        return self.bpe.process_line(text)


class ProcessorChain(TextProcessor):
    """
    A list of text processors that run sequentially
    """

    def __init__(self, chain: List[TextProcessor]):
        super().__init__()

        self.chain = chain

    def run(self, text: str) -> str:
        for processor in self.chain:
            text = processor.run(text)
        return text


class DeBPE(TextProcessor):
    """
    Removes BPE
    """

    def __init__(self):
        super().__init__()

        self.de_bpe = re.compile('@@( |$)', re.IGNORECASE)

    def run(self, text):
        return re.sub(self.de_bpe, '', text).strip()


class Detokenizer(TextProcessor):
    """
    Detokenizes text
    """

    def __init__(self, scripts_path):
        super().__init__()

        self.de_tok = os.path.join(scripts_path, 'detokenize.pl')

        if not os.access(self.de_tok, os.X_OK):
            os.chmod(self.de_tok, 0o755)

    def run(self, text):
        return run_subprocess(text, [self.de_tok, '-l', 'en'])
