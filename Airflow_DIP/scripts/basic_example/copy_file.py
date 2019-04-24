import argparse
from shutil import copyfile

def run(parsed_args):
    copyfile(parsed_args.input, parsed_args.output)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--output', type=str)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    if parsed_args.dry_run:
        return {
            'inputs': [parsed_args.input],
            'outputs': [parsed_args.output]
        }
    else:
        run(parsed_args)

if __name__=='__main__':
    print(main())
