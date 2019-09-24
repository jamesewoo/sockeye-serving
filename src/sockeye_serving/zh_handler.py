import os
import pkg_resources
import regex as re
import unicodedata

from .default_handler import DefaultPreprocessor
from .sockeye_handler import SockeyeHandler
from .text_processor import BpeEncoder, DeBPE, Detokenizer, ProcessorChain
from .utils import run_subprocess


class ChinesePreprocessor(DefaultPreprocessor):
    """
    Preprocesses Chinese text
    """

    def __init__(self, scripts_path):
        super().__init__(scripts_path, 'zh')

        self.pattern = re.compile(
            r'([\p{IsHan}\p{InCJK_Symbols_and_Punctuation}\p{InCJK_Radicals_Supplement}\p{InCJK_Compatibility}])',
            re.UNICODE)

    def run(self, text):
        text = self.unescape(text)
        text = unicodedata.normalize('NFKC', text)
        text = self.remove_control_characters(text)

        # tokenize by separating all ZH characters with a space
        return self.pattern.sub(r' \1 ', text).strip()


class ChineseHandler(SockeyeHandler):
    """
    Consumes Chinese text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)
        scripts_path = pkg_resources.resource_filename(
            'sockeye_serving', 'scripts')
        bpe_codes = os.path.join(self.basedir, 'bpe-codes.txt')

        preprocessors = [ChinesePreprocessor(scripts_path)]
        if os.path.isfile(bpe_codes):
            preprocessors.append(BpeEncoder(bpe_codes))

        self.preprocessor = ProcessorChain(preprocessors)
        self.postprocessor = DeBPE()


_service = ChineseHandler()


def handle(data, context):
    return _service.handle(data, context)
