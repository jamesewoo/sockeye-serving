import os

import pkg_resources
import unicodedata

from .sockeye_handler import SockeyeHandler
from .text_processor import BpeEncoder, DeBPE, Detokenizer, ProcessorChain, TextProcessor
from .utils import run_subprocess


class DefaultPreprocessor(TextProcessor):
    """
    A preprocessor that uses Joshua scripts to preprocess text
    """

    def __init__(self, scripts_path, lang):
        super().__init__()

        self.lang = lang
        self.tokenizer = os.path.join(scripts_path, 'tokenizer.perl')

        if not os.access(self.tokenizer, os.X_OK):
            os.chmod(self.tokenizer, 0o755)

    def run(self, text):
        text = self.unescape(text)
        text = unicodedata.normalize('NFKC', text)
        text = self.remove_control_characters(text)

        return run_subprocess(
            text, [self.tokenizer, '-l', self.lang, '-no-escape', '-q'])


class DefaultHandler(SockeyeHandler):
    """
    Consumes text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)

        scripts_path = pkg_resources.resource_filename(
            'sockeye_serving', 'scripts')
        # get the language from the model name
        lang = context.model_name

        bpe_codes = os.path.join(self.basedir, 'bpe-codes.txt')
        preprocessors = [DefaultPreprocessor(scripts_path, lang)]
        if os.path.isfile(bpe_codes):
            preprocessors.append(BpeEncoder(bpe_codes))
        self.preprocessor = ProcessorChain(preprocessors)

        postprocessors = [DeBPE(), Detokenizer(scripts_path)]
        self.postprocessor = ProcessorChain(postprocessors)


_service = DefaultHandler()


def handle(data, context):
    return _service.handle(data, context)
