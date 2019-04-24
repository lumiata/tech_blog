import argparse
import pathlib
import tensorflow as tf

from scripts.embedding_example.config import (
    DEFAULT_KERAS_SUBDIR, DEFAULT_KERAS_DIR)

def run(inputs, cache_dir):
    for url in inputs:
        tf.keras.utils.get_file(
            url.split('/')[-1], url, cache_dir=cache_dir)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-url', type=str)
    parser.add_argument('--test-url', type=str)
    parser.add_argument('--cache-dir', type=str, default=DEFAULT_KERAS_DIR)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    inputs = [parsed_args.train_url, parsed_args.test_url]
    if parsed_args.dry_run:
        target_path = (
                pathlib.Path(parsed_args.cache_dir) / DEFAULT_KERAS_SUBDIR)
        outputs = [str((target_path / url.split('/')[-1]).expanduser()) for url in inputs]
        return {
            'inputs': inputs,
            'outputs': outputs
        }
    else:
        run(inputs, parsed_args.cache_dir)

if __name__=='__main__':
    print(main())