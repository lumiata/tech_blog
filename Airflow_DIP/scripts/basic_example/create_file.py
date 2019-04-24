import argparse

def run(parsed_args):
    with open(parsed_args.output, 'w') as f:
        f.write('test pipeline')

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    if parsed_args.dry_run:
        return {
            'outputs': [parsed_args.output]
        }
    else:
        run(parsed_args)

if __name__=='__main__':
    print(main())
