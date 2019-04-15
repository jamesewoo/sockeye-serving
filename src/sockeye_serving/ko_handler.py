import pkg_resources
import regex as re

from .sockeye_handler import SockeyeHandler
from .text_processor import JoshuaPreprocessor, Detokenizer
from .utils import run_subprocess


class KoreanPreprocessor(JoshuaPreprocessor):
    """
    Preprocesses Korean text
    """

    def __init__(self, scripts_path):
        super().__init__(scripts_path, 'ko')

        self.pattern = re.compile('([\uac00-\ud7a3])', re.UNICODE)

    def run(self, text):
        text = self.unescape(text)

        # normalize and remove non-printing characters
        text = run_subprocess(text, [self.normalizer, self.lang, '|', self.cleaner])

        # tokenize by separating all KO characters with a space
        text = self.pattern.sub(r' \1 ', text).strip()

        # tokenize other characters using Moses
        return run_subprocess(text, [self.tokenizer, '-l', self.lang, '-no-escape', '-q'])


class KoreanHandler(SockeyeHandler):
    """
    Consumes Korean text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)
        scripts_path = pkg_resources.resource_filename('sockeye_serving', 'scripts')
        self.preprocessor = KoreanPreprocessor(scripts_path)
        self.postprocessor = Detokenizer(scripts_path)


_service = KoreanHandler()


def handle(data, context):
    return _service.handle(data, context)
