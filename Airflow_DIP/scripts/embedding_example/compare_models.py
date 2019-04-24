import argparse

def get_accuracy(report):
    with open(report) as f:
        model = None
        for line in f:
            if not model:
                model = line.strip()
            if line.startswith('Test set metrics'):
                break
        for line in f:
            if line.startswith('accuracy'):
                return model, float(line.split()[1])

def run(model_reports, output):
    model, accuracy = None, 0.0
    for report in model_reports:
        new_model, new_accuracy = get_accuracy(report)
        if new_accuracy > accuracy:
            model, accuracy = new_model, new_accuracy
    result = f'best_model: {model}\naccuracy: {accuracy}'
    print(result)
    with open(output, 'w') as f:
        f.write(result)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False)
    parser.add_argument('--model-reports', nargs='+', type=str)
    parser.add_argument('--output', type=str)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    if parsed_args.dry_run:
        return {
            'inputs': parsed_args.model_reports,
            'outputs': [parsed_args.output]
        }
    else:
        run(parsed_args.model_reports, parsed_args.output)

if __name__=='__main__':
    print(main())