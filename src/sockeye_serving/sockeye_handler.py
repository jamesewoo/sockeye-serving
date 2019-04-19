# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#     http://www.apache.org/licenses/LICENSE-2.0
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.


import logging
import os
from contextlib import ExitStack

from sockeye import arguments
from sockeye import constants as const
from sockeye import inference
from sockeye.lexicon import TopKLexicon
from sockeye.output_handler import get_output_handler
from sockeye.utils import check_condition, log_basic_info, determine_context

from .utils import decode_bytes, get_file_data, get_text, read_sockeye_args


class SockeyeHandler(object):
    """
    Consumes text of arbitrary length and returns its translation.
    """

    def __init__(self):
        self._context = None
        self._batch_size = 0
        self.error = None
        self.basedir = None
        self.initialized = False
        self.postprocessor = None
        self.preprocessor = None
        self.sentence_id = 0
        self.translator = None

    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time

        :param context: Initial context contains model server system properties.
        :return:
        """
        self._context = context
        self._batch_size = context.system_properties['batch_size']
        self.basedir = context.system_properties['model_dir']
        self.translator = self.get_translator(context)
        self.initialized = True

    def get_translator(self, context):
        """
        Returns a translator for the given context
        :param context: model server context
        :return:
        """
        params = arguments.ConfigArgumentParser(description='Translate CLI')
        arguments.add_translate_cli_args(params)

        sockeye_args_path = os.path.join(self.basedir, 'sockeye-args.txt')
        sockeye_args = params.parse_args(read_sockeye_args(sockeye_args_path))
        # override models directory
        sockeye_args.models = [self.basedir]

        device_ids = []
        if 'gpu_id' in context.system_properties:
            device_ids.append(context.system_properties['gpu_id'])
        else:
            logging.warning('No gpu_id found in context')
            device_ids.append(0)

        log_basic_info(sockeye_args)

        if sockeye_args.nbest_size > 1:
            if sockeye_args.output_type != const.OUTPUT_HANDLER_JSON:
                logging.warning(f'For n-best translation, you must specify --output-type {const.OUTPUT_HANDLER_JSON}')
                sockeye_args.output_type = const.OUTPUT_HANDLER_JSON

        output_handler = get_output_handler(sockeye_args.output_type,
                                            sockeye_args.output,
                                            sockeye_args.sure_align_threshold)

        with ExitStack() as exit_stack:
            check_condition(len(device_ids) == 1, 'translate only supports single device for now')
            translator_ctx = determine_context(device_ids=device_ids,
                                               use_cpu=sockeye_args.use_cpu,
                                               disable_device_locking=sockeye_args.disable_device_locking,
                                               lock_dir=sockeye_args.lock_dir,
                                               exit_stack=exit_stack)[0]
            logging.info(f'Translate Device: {translator_ctx}')

            models, source_vocabs, target_vocab = inference.load_models(
                context=translator_ctx,
                max_input_len=sockeye_args.max_input_len,
                beam_size=sockeye_args.beam_size,
                batch_size=sockeye_args.batch_size,
                model_folders=sockeye_args.models,
                checkpoints=sockeye_args.checkpoints,
                softmax_temperature=sockeye_args.softmax_temperature,
                max_output_length_num_stds=sockeye_args.max_output_length_num_stds,
                decoder_return_logit_inputs=sockeye_args.restrict_lexicon is not None,
                cache_output_layer_w_b=sockeye_args.restrict_lexicon is not None,
                override_dtype=sockeye_args.override_dtype,
                output_scores=output_handler.reports_score(),
                sampling=sockeye_args.sample)

            restrict_lexicon = None
            if sockeye_args.restrict_lexicon is not None:
                logging.info(str(sockeye_args.restrict_lexicon))
                if len(sockeye_args.restrict_lexicon) == 1:
                    # Single lexicon used for all inputs
                    restrict_lexicon = TopKLexicon(source_vocabs[0], target_vocab)
                    # Handle a single arg of key:path or path (parsed as path:path)
                    restrict_lexicon.load(sockeye_args.restrict_lexicon[0][1], k=sockeye_args.restrict_lexicon_topk)
                else:
                    check_condition(sockeye_args.json_input,
                                    'JSON input is required when using multiple lexicons for vocabulary restriction')
                    # Multiple lexicons with specified names
                    restrict_lexicon = dict()
                    for key, path in sockeye_args.restrict_lexicon:
                        lexicon = TopKLexicon(source_vocabs[0], target_vocab)
                        lexicon.load(path, k=sockeye_args.restrict_lexicon_topk)
                        restrict_lexicon[key] = lexicon

            store_beam = sockeye_args.output_type == const.OUTPUT_HANDLER_BEAM_STORE

            brevity_penalty_weight = sockeye_args.brevity_penalty_weight
            if sockeye_args.brevity_penalty_type == const.BREVITY_PENALTY_CONSTANT:
                if sockeye_args.brevity_penalty_constant_length_ratio > 0.0:
                    constant_length_ratio = sockeye_args.brevity_penalty_constant_length_ratio
                else:
                    constant_length_ratio = sum(model.length_ratio_mean for model in models) / len(models)
                    logging.info(
                        f'Using average of constant length ratios saved in the model configs: {constant_length_ratio}')
            elif sockeye_args.brevity_penalty_type == const.BREVITY_PENALTY_LEARNED:
                constant_length_ratio = -1.0
            elif sockeye_args.brevity_penalty_type == const.BREVITY_PENALTY_NONE:
                brevity_penalty_weight = 0.0
                constant_length_ratio = -1.0
            else:
                raise ValueError(f'Unknown brevity penalty type {sockeye_args.brevity_penalty_type}')

            brevity_penalty = None
            if brevity_penalty_weight != 0.0:
                brevity_penalty = inference.BrevityPenalty(brevity_penalty_weight)

            return inference.Translator(context=translator_ctx,
                                        ensemble_mode=sockeye_args.ensemble_mode,
                                        bucket_source_width=sockeye_args.bucket_width,
                                        length_penalty=inference.LengthPenalty(sockeye_args.length_penalty_alpha,
                                                                               sockeye_args.length_penalty_beta),
                                        beam_prune=sockeye_args.beam_prune,
                                        beam_search_stop=sockeye_args.beam_search_stop,
                                        nbest_size=sockeye_args.nbest_size,
                                        models=models,
                                        source_vocabs=source_vocabs,
                                        target_vocab=target_vocab,
                                        restrict_lexicon=restrict_lexicon,
                                        avoid_list=sockeye_args.avoid_list,
                                        store_beam=store_beam,
                                        strip_unknown_words=sockeye_args.strip_unknown_words,
                                        skip_topk=sockeye_args.skip_topk,
                                        sample=sockeye_args.sample,
                                        constant_length_ratio=constant_length_ratio,
                                        brevity_penalty=brevity_penalty)

    def preprocess(self, batch):
        """
        Preprocesses a JSON request for translation.

        :param batch: a list of JSON requests of the form { 'text': input_string } or { 'file': file_data }
        :return: a list of input strings to translate
        """
        texts = []
        for req in batch:
            data = get_file_data(req)

            if data:
                text = decode_bytes(data)
            else:
                text = get_text(req)

            if text:
                t = self.preprocessor.run(text)
                texts.append(t)

        return texts

    def inference(self, texts):
        """
        Translates the input data.

        :param texts: a list of strings to translate
        :return: a list of translation objects from Sockeye
        """
        if texts:
            trans_inputs = []
            for t in texts:
                _input = inference.make_input_from_plain_string(self.sentence_id, t)
                trans_inputs.append(_input)
            outputs = self.translator.translate(trans_inputs)

            if len(outputs) != len(trans_inputs):
                logging.warning("Number of translation outputs doesn't match the number of inputs")

            self.sentence_id += len(trans_inputs)
            return outputs
        else:
            self.error = 'Input to inference is empty'
            return []

    def postprocess(self, outputs):
        """
        Converts the translations into a list of JSON responses.

        :param outputs: a list of translation objects from Sockeye
        :return: a list of translations of the form: { 'translation': output_string }
        """
        res = []
        for output in outputs:
            translation = self.postprocessor.run(output.translation)
            res.append({'translation': translation})
        return res

    def handle(self, data, context):
        """
        Custom service entry point function.

        :param data: list of objects, raw input from request
        :param context: model server context
        :return: list of outputs to be send back to client
        """

        if not self.initialized:
            self.initialize(context)

        if data is None:
            return None

        try:
            data = self.preprocess(data)
            data = self.inference(data)
            data = self.postprocess(data)
            return data

        except Exception as e:
            logging.error(e, exc_info=True)
            request_processor = context.request_processor
            request_processor.report_status(500, "Unknown inference error")
            return [str(e)] * self._batch_size
