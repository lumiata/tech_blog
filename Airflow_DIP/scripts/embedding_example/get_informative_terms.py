import argparse
import tensorflow as tf
import io
import pathlib

from scripts.embedding_example.config import (
    DEFAULT_KERAS_SUBDIR, DEFAULT_KERAS_DIR, DEFAULT_TERMS, TERMS_FILENAME)


def run(url, output):
    output = output.expanduser()
    if url:
        tf.keras.utils.get_file(output, url)
    else:
        with io.open(output, 'w', encoding='utf-8') as f:
            f.write(' '.join(DEFAULT_TERMS))

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False)
    parser.add_argument('--terms-filename', type=str, default=TERMS_FILENAME)
    parser.add_argument('--cache-dir', type=str, default=DEFAULT_KERAS_DIR)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    inputs = [] if parsed_args.url is None else [parsed_args.url]
    output = pathlib.Path(
        parsed_args.cache_dir
    ) / DEFAULT_KERAS_SUBDIR / parsed_args.terms_filename
    output = output.expanduser()
    if parsed_args.dry_run:
        return {
            'inputs': inputs,
            'outputs': [str(output)]
        }
    else:
        run(parsed_args.url, output)

if __name__=='__main__':
    print(main())
