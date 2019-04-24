import argparse

import io
import tensorflow as tf
from scripts.embedding_example.util import (
    get_embedding_columns, _input_fn)
from dags.lib import normalize_path

def run(parsed_args):
    hyper = parsed_args
    informative_terms = normalize_path(parsed_args.informative_terms)
    train_input = normalize_path(parsed_args.train_input)
    test_input = normalize_path(parsed_args.test_input)

    feature_columns = [
        get_embedding_columns(informative_terms, hyper.dimension)]
    model_checkpoint = tf.train.latest_checkpoint(parsed_args.model_folder)

    classifier = tf.estimator.DNNClassifier(
        feature_columns=feature_columns,
        hidden_units=hyper.hidden_units,
        warm_start_from=model_checkpoint
    )
    report = []
    evaluation_metrics = classifier.evaluate(
        input_fn=lambda: _input_fn([train_input]),
        steps=1000)
    report.append(parsed_args.model_folder)
    report.append('---')
    report.append('Training set metrics:')
    for m in evaluation_metrics:
        report.append(f'{m} {evaluation_metrics[m]}')
    report.append('---')

    evaluation_metrics = classifier.evaluate(
        input_fn=lambda: _input_fn([test_input]),
        steps=1000)

    report.append('Test set metrics:')
    for m in evaluation_metrics:
        report.append(f'{m} {evaluation_metrics[m]}')
    report.append('---')
    for line in report:
        print(line)
    with io.open(parsed_args.output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-input', type=str)
    parser.add_argument('--test-input', type=str)
    parser.add_argument('--model-folder', type=str)
    parser.add_argument('--informative-terms', type=str)
    hyper_group = parser.add_argument_group('hyper')
    hyper_group.add_argument('--dimension', '-d',
                             type=int, default=2)
    hyper_group.add_argument('--hidden-units', '-hu',
                             nargs='+', default=[10, 10], type=int)
    parser.add_argument('--output', type=str)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    if parsed_args.dry_run:
        return {
            'inputs': [parsed_args.train_input, parsed_args.test_input,
                       parsed_args.model_folder,
                       parsed_args.informative_terms],
            'outputs': [parsed_args.output]
        }
    else:
        run(parsed_args)

if __name__=='__main__':
    print(main())