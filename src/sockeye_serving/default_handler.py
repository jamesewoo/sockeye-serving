import os

import pkg_resources

from .sockeye_handler import SockeyeHandler
from .text_processor import Detokenizer, JoshuaPreprocessor, ProcessorChain, BpeEncoder


class DefaultHandler(SockeyeHandler):
    """
    Consumes text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)

        scripts_path = pkg_resources.resource_filename('sockeye_serving', 'scripts')
        # get the language from the model name
        lang = context.model_name

        bpe_codes = os.path.join(self.basedir, 'bpe-codes.txt')
        preprocessors = [JoshuaPreprocessor(scripts_path, lang)]
        if os.path.isfile(bpe_codes):
            preprocessors.append(BpeEncoder(bpe_codes))

        self.preprocessor = ProcessorChain(preprocessors)
        self.postprocessor = Detokenizer(scripts_path)


_service = DefaultHandler()


def handle(data, context):
    return _service.handle(data, context)
