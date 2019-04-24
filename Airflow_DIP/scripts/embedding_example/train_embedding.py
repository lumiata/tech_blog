import argparse
import tensorflow as tf
from scripts.embedding_example.util import (
    get_embedding_columns, _input_fn)
from dags.lib import normalize_path

def run(parsed_args):
    # creating an alias to distinguish the two type of arguments
    hyper = parsed_args
    informative_terms = normalize_path(parsed_args.informative_terms)
    input = normalize_path(parsed_args.input)
    feature_columns = [
        get_embedding_columns(informative_terms, hyper.dimension)]

    my_optimizer = tf.train.AdagradOptimizer(learning_rate=hyper.learning_rate)
    my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer,
                                                               hyper.gradient_clipping)

    classifier = tf.estimator.DNNClassifier(
        feature_columns=feature_columns,
        hidden_units=hyper.hidden_units,
        optimizer=my_optimizer,
        model_dir=parsed_args.output
    )

    classifier.train(
        input_fn=lambda: _input_fn([input]),
        steps=1000)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--informative-terms', type=str)
    hyper_group = parser.add_argument_group('hyper')
    hyper_group.add_argument('--dimension', '-d',
                             type=int, default=2)
    hyper_group.add_argument('--learning-rate', '-l',
                             type=float, default=0.1)
    hyper_group.add_argument('--gradient-clipping', '-gc',
                             type=float, default=5.0)
    hyper_group.add_argument('--hidden-units', '-hu', nargs='+', default=[10, 10], type=int)
    parser.add_argument('--output', type=str)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    if parsed_args.dry_run:
        return {
            'inputs': [parsed_args.input, parsed_args.informative_terms],
            'outputs': [parsed_args.output]
        }
    else:
        run(parsed_args)

if __name__=='__main__':
    print(main())
