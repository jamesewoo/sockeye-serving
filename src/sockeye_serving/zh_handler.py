import pkg_resources
import regex as re

from .sockeye_handler import SockeyeHandler
from .text_processor import JoshuaPreprocessor, Detokenizer
from .utils import run_subprocess


class ChineseCharPreprocessor(JoshuaPreprocessor):
    """
    Preprocesses Chinese text
    """

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


class ChineseHandler(SockeyeHandler):
    """
    Consumes Chinese text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)
        scripts_path = pkg_resources.resource_filename('sockeye_serving', 'scripts')
        self.preprocessor = ChineseCharPreprocessor(scripts_path)
        self.postprocessor = Detokenizer(scripts_path)


_service = ChineseHandler()


def handle(data, context):
    return _service.handle(data, context)
