import os

import pytest
from mms.context import Context

from sockeye_serving import sockeye_handler, default_handler, ko_handler, zh_handler


@pytest.fixture
def my_ctx():
    model_dir = os.path.join(os.path.dirname(__file__), 'resources')
    return Context(model_name='test',
                   model_dir=model_dir,
                   manifest='manifest',
                   batch_size=1,
                   gpu=0,
                   mms_version='1.0.3')


def run_test(handler: sockeye_handler.SockeyeHandler, context: Context):
    handler.initialize(context)
    assert handler.initialized
    assert handler.translator
    assert handler.preprocessor
    assert handler.postprocessor

    response = handler.handle([{'body': 'a b c 123'}], context)
    assert len(response) == 1
    assert response[0].get('translation')


def test_default_handler(my_ctx):
    run_test(default_handler.DefaultHandler(), my_ctx)


def test_ko_handler(my_ctx):
    run_test(ko_handler.KoreanHandler(), my_ctx)


def test_zh_handler(my_ctx):
    run_test(zh_handler.ChineseHandler(), my_ctx)
